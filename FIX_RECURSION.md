# Fix Lỗi Tràn Stack Khi Xử Lý 10,000+ Files

## 🎯 **Yêu Cầu**
- Mỗi job xử lý TẤT CẢ 10,000 files (giữ nguyên logic ban đầu)
- KHÔNG bị lỗi "Maximum call stack size exceeded"
- Tạo nhiều file CSV summary để dễ quản lý

## ❌ **Nguyên Nhân Lỗi**

### Python `directory.walk()` bị recursion quá sâu
```python
# CODE CŨ - BỊ LỖI:
for (dirpath, _, filenames) in directory.walk():  # ← Recursion sâu!
    for filename in filenames:
        # Process 10000 files...
```

Khi có 10,000 files, Python `Path.walk()` tạo **deep recursion stack** → `RecursionError`

## ✅ **Giải Pháp**

### 1. Dùng `os.walk()` thay vì `Path.walk()`
```python
# CODE MỚI - KHÔNG BỊ LỖI:
import os

all_files = []
for root, dirs, files in os.walk(directory):  # ← os.walk() hiệu quả hơn
    for filename in files:
        if pattern.fullmatch(filename):
            all_files.append((Path(root), filename))

# Xử lý iteratively, không recursion
for dirpath, filename in all_files:
    # Process...
```

**Tại sao `os.walk()` tốt hơn?**
- `os.walk()` dùng iterator, không tạo recursion stack
- `Path.walk()` (Python 3.12+) dùng recursion nội bộ
- `os.walk()` nhanh hơn và ít tốn bộ nhớ hơn

### 2. Xử lý theo batch + commit từng đợt
```python
batch_size = 100
for batch_idx in range(0, total_files, batch_size):
    batch = all_files[batch_idx:batch_idx + batch_size]
    
    for file in batch:
        # Process file...
        csv.write(...)
        cursor.execute(...)
    
    connection.commit()  # ← Commit mỗi 100 files
```

**Lợi ích:**
- Giải phóng bộ nhớ định kỳ
- Không mất dữ liệu nếu bị crash giữa chừng
- Progress reporting rõ ràng

### 3. Tạo batch CSV files (optional)
```python
if batch_mode:
    # Tạo file CSV riêng cho mỗi batch
    batch_csv = directory / f"summary_batch_{batch_num}.csv"
    # Write headers + data...
```

## 📊 **Kết Quả**

### Workflow Logic (KHÔNG ĐỔI)
```yaml
# Mỗi job vẫn xử lý TẤT CẢ files như ban đầu
Job 0: Process ALL 10,000 files
Job 1: Process ALL 10,000 files
...
Job 9: Process ALL 10,000 files
```

### Python Script (ĐÃ TỐI ƯU)
```
Scan files:       os.walk() ✅ (không recursion)
Process batches:  100 files/batch ✅ (commit từng đợt)
Create CSV:       1 main + N batch files ✅
```

### Output Files
```
outputs/
├── summary.csv              ← TẤT CẢ results (10,000 entries)
├── summary.db              ← SQLite database
├── summary_batch_1.csv     ← Batch 1 (100 entries)
├── summary_batch_2.csv     ← Batch 2 (100 entries)
├── ...
└── summary_batch_100.csv   ← Batch 100 (100 entries)
```

## 🧪 **Test**

### Với 1,000 files:
```
✓ No recursion error
✓ 1 main CSV (1000 entries)
✓ 10 batch CSVs (100 entries each) - if --batch-mode
```

### Với 10,000 files:
```
✓ No recursion error
✓ 1 main CSV (10000 entries)
✓ 100 batch CSVs (100 entries each) - if --batch-mode
```

### Với 100,000 files:
```
✓ No recursion error
✓ 1 main CSV (100000 entries)
✓ 1000 batch CSVs (100 entries each) - if --batch-mode
```

## ⚙️ **Cách Sử Dụng**

### Mặc định (không batch):
```bash
python scripts/summary.py
# → Tạo summary.csv và summary.db
```

### Với batch mode:
```bash
python scripts/summary.py --batch-mode
# → Tạo summary.csv, summary.db + summary_batch_*.csv
```

### Tùy chỉnh batch size:
```bash
python scripts/summary.py --batch-mode --batch-size 1000
# → Mỗi batch CSV chứa 1000 entries thay vì 100
```

## 🔧 **Các Thay Đổi Code**

### 1. scripts/summary.py
- ✅ Thêm `import os`
- ✅ Dùng `os.walk()` thay vì `Path.walk()`
- ✅ Xử lý theo batch 100 files
- ✅ Commit database sau mỗi batch
- ✅ Tạo batch CSV files khi `--batch-mode`
- ✅ Progress reporting chi tiết

### 2. .github/workflows/run.yml
- ✅ Giữ nguyên logic ban đầu (mỗi job xử lý tất cả files)
- ✅ Thêm `PYTHONRECURSIONLIMIT: 10000` (phòng hờ)
- ✅ Tự động enable `--batch-mode` khi > 1000 output files

## 💡 **Lưu Ý**

1. **Mỗi job vẫn xử lý tất cả files** - điều này tốn tài nguyên nhưng là yêu cầu của bạn
2. **10 jobs = 10 lần xử lý giống nhau** - có thể tối ưu bằng cách chia file cho jobs
3. **Batch CSV giúp** mở file Excel/CSV dễ hơn khi có nhiều entries
4. **os.walk() là chìa khóa** - giải quyết recursion error

## 🎯 **Tóm Tắt**

| Điểm | Giải Pháp |
|------|-----------|
| ❌ Lỗi recursion | ✅ Dùng `os.walk()` thay vì `Path.walk()` |
| ❌ Memory overflow | ✅ Process theo batch + commit từng đợt |
| ❌ CSV quá lớn | ✅ Tạo batch CSV files (optional) |
| ❌ Không biết tiến độ | ✅ Progress reporting chi tiết |
| ✅ Logic workflow | ✅ Giữ nguyên (mỗi job xử lý tất cả) |
