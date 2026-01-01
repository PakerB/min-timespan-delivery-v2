# Các Thay Đổi Để Fix Lỗi Tràn Bộ Nhớ

## Vấn Đề
Khi push 5000-10000 file test, workflow bị lỗi "Maximum call stack size exceeded" do:
1. Quá nhiều file được xử lý cùng lúc
2. Python summary script bị tràn stack khi duyệt thư mục
3. Không có giới hạn số file xử lý trong mỗi job

## Giải Pháp Đã Áp Dụng

### 1. Cập nhật README.md
- **Thay đổi**: Đổi link từ `Serious-senpai` sang `PakerB`
- **File**: `README.md` line 5
- **Lý do**: Độc lập với repo gốc

### 2. Cập nhật GitHub Actions Workflow
- **File**: `.github/workflows/run.yml`

#### a. Thay custom action bằng official action
```yaml
# Trước:
uses: Serious-senpai/download-artifact@patch-1

# Sau:
uses: actions/download-artifact@v4
```
**Lý do**: Official v4 đã hỗ trợ `merge-multiple`, không phụ thuộc repo người khác

#### b. Giới hạn số file xử lý mỗi job
```bash
max_files_per_job=500  # Mỗi job chỉ xử lý tối đa 500 file
```
**Lý do**: Tránh quá tải bộ nhớ khi có hàng ngàn file

#### c. Tăng Python recursion limit
```yaml
env:
  PYTHONRECURSIONLIMIT: 10000
```
**Lý do**: Python mặc định có limit 1000, không đủ cho nhiều file

### 3. Cải thiện Python Summary Script
- **File**: `scripts/summary.py`

#### a. Tăng sys.setrecursionlimit
```python
sys.setrecursionlimit(10000)
```

#### b. Xử lý file theo batch
```python
# Collect tất cả file trước để tránh recursion trong directory.walk()
all_files = []
for (dirpath, _, filenames) in directory.walk():
    for filename in filenames:
        if pattern.fullmatch(filename):
            all_files.append((dirpath, filename))

# Xử lý từng batch 100 file
batch_size = 100
for batch_idx in range(0, len(all_files), batch_size):
    batch = all_files[batch_idx:batch_idx + batch_size]
    # Process batch...
    connection.commit()  # Commit sau mỗi batch
```

**Lý do**: 
- Tránh recursion sâu khi duyệt thư mục
- Quản lý bộ nhớ tốt hơn với batch processing
- Commit từng batch để tránh mất dữ liệu

## Kết Quả Mong Đợi

### Trước Fix
- ❌ 1000 file: OK
- ❌ 5000 file: FAIL (stack overflow)
- ❌ 10000 file: FAIL (stack overflow)

### Sau Fix
- ✅ 1000 file: OK
- ✅ 5000 file: OK (chia thành 10 jobs × 500 file)
- ✅ 10000 file: OK (chia thành 10 jobs × 500 file, hoặc 20 jobs nếu cần)

## Cách Tăng Capacity Nếu Cần

### Để xử lý nhiều file hơn trong 1 workflow run:

1. **Tăng số matrix jobs** trong `.github/workflows/run.yml`:
```yaml
matrix:
  steps: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
  # 10 jobs → 20 jobs = 10000 files capacity
```

2. **Tăng max_files_per_job**:
```bash
max_files_per_job=1000  # Nếu muốn mỗi job xử lý nhiều hơn
```

3. **Tăng batch_size** trong `summary.py`:
```python
batch_size = 200  # Xử lý 200 file mỗi batch thay vì 100
```

## Lưu Ý Quan Trọng

### GitHub Actions Limits:
- Maximum 256 matrix jobs per workflow
- 6 hours timeout mỗi job
- 10 GB disk space mỗi runner

### Khuyến Nghị:
- Với 10000 file: Dùng 20 jobs × 500 file = OK
- Với 50000 file: Cần chia thành nhiều workflow runs
- Monitor memory usage trong job logs

## Testing

Sau khi thay đổi, test như sau:

1. **Test với 1000 file** (nên pass):
```bash
# Trong generate_instance.py
batch_size = 1000
start_number = 1
```

2. **Test với 5000 file**:
```bash
batch_size = 5000
start_number = 1
```

3. **Test với 10000 file**:
```bash
batch_size = 10000
start_number = 1
```

Push lên GitHub và kiểm tra workflow runs.

## Rollback Plan

Nếu có vấn đề, restore bằng cách:
1. Revert commit này
2. Hoặc thay đổi lại trong `run.yml`:
   - Giảm `max_files_per_job` xuống 100
   - Tăng số matrix jobs lên 50-100
