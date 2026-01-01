# Hướng Dẫn Chạy 10,000 Files Với GitHub Actions

## 🎯 **Vấn Đề**

### **Logic Algorithm:**
- Mỗi file cần chạy **10 lần** (10 jobs) để tìm kết quả tối ưu nhất
- 10,000 files × 10 jobs × 20 phút/file = **33,333 giờ** = KHÔNG THỂ!

### **GitHub Actions Limit:**
- ⏰ **6 giờ** timeout per job
- 📦 **10 GB** artifact size limit
- 🔢 **256** jobs max trong 1 workflow

## ✅ **GIẢI PHÁP: CHIA BATCH**

### **Chiến Lược:**
```
10,000 files chia thành 10 batch × 1,000 files/batch

Batch 1: Files 1-1000     → 10 jobs × 1000 files
Batch 2: Files 1001-2000  → 10 jobs × 1000 files
...
Batch 10: Files 9001-10000 → 10 jobs × 1000 files
```

## 📋 **CÁCH SỬ DỤNG**

### **Bước 1: Push 10,000 Files Lên GitHub**

```powershell
cd problems
python generate_instance.py  # Sinh 10,000 files

cd ..
git add problems/data/*.txt
git commit -m "Add 10000 test files"
git push
```

### **Bước 2: Chạy Batch Workflow (Manual)**

1. Vào GitHub repo: `https://github.com/PakerB/min-timespan-delivery-v2`

2. Click tab **Actions**

3. Chọn workflow **"Run algorithm (Batched)"**

4. Click **"Run workflow"**

5. Nhập parameters:
   ```
   batch_number: 1          ← Batch nào (1-10)
   files_per_batch: 1000    ← Số files mỗi batch
   ```

6. Click **"Run workflow"** xanh

7. **LẶP LẠI** cho Batch 2, 3, 4, ..., 10

### **Bước 3: Tự Động Hóa (Optional)**

Tạo script Python để tự động trigger các batches:

```python
# trigger_batches.py
import requests
import os

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO = 'PakerB/min-timespan-delivery-v2'

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

for batch in range(1, 11):  # Batch 1-10
    url = f'https://api.github.com/repos/{REPO}/actions/workflows/run-batch.yml/dispatches'
    data = {
        'ref': 'main',
        'inputs': {
            'batch_number': str(batch),
            'files_per_batch': '1000'
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Triggered batch {batch}: {response.status_code}")
```

Chạy:
```powershell
$env:GITHUB_TOKEN = "your_github_token"
python trigger_batches.py
```

## 📊 **KẾT QUẢ**

### **Sau Khi Chạy Xong 10 Batches:**

```
Artifacts:
├── summary-batch-1.csv    (Batch 1 results)
├── summary-batch-2.csv    (Batch 2 results)
...
└── summary-batch-10.csv   (Batch 10 results)
```

### **Merge Các Batch:**

```python
# merge_batches.py
import pandas as pd

dfs = []
for i in range(1, 11):
    df = pd.read_csv(f'summary-batch-{i}.csv', sep=',', skiprows=1)
    dfs.append(df)

merged = pd.concat(dfs, ignore_index=True)
merged.to_csv('summary-complete.csv', index=False)
print(f"Merged {len(merged)} results")
```

## ⏱️ **THỜI GIAN ƯỚC TÍNH**

| Metric | Per Batch | Total (10 Batches) |
|--------|-----------|-------------------|
| Files | 1,000 | 10,000 |
| Jobs | 10 | 100 |
| Time/file | 20 phút | 20 phút |
| Total time | ~5-6 giờ | ~50-60 giờ |
| Can run parallel | ✅ Yes | Giảm xuống ~6 giờ |

**Nếu chạy tuần tự:** 10 batches × 6 giờ = 60 giờ = 2.5 ngày
**Nếu chạy song song:** Tất cả cùng lúc = 6 giờ

## 🚀 **TỐI ƯU HÓA**

### **Chạy Nhiều Batch Đồng Thời:**

```python
# Trigger 5 batches cùng lúc
for batch in range(1, 6):
    trigger_batch(batch)

# Đợi xong, trigger 5 batch còn lại
for batch in range(6, 11):
    trigger_batch(batch)
```

### **Tăng Files Per Batch:**

Nếu files nhỏ, có thể tăng lên 2000 files/batch:
```yaml
batch_number: 1
files_per_batch: 2000  # 10k files = 5 batches
```

## 📝 **TÓM TẮT**

### **Workflow Cũ (run.yml):**
- ❌ Xử lý TẤT CẢ files mỗi lần push
- ❌ Timeout sau 6 giờ khi có nhiều files
- ❌ Không kiểm soát được số files

### **Workflow Mới (run-batch.yml):**
- ✅ Chia thành batches nhỏ
- ✅ Manual trigger, kiểm soát từng batch
- ✅ Mỗi batch < 6 giờ = không timeout
- ✅ Có thể chạy song song nhiều batch

## 🔧 **COMMIT VÀ SỬ DỤNG**

```powershell
git add .github/workflows/run-batch.yml
git commit -m "Add batched workflow for processing 10k+ files

- New workflow: run-batch.yml with manual trigger
- Input parameters: batch_number, files_per_batch
- Each batch processes 1000 files (configurable)
- 10k files = 10 batches, can run in parallel
- No timeout issues, better control"

git push
```

**Sau đó vào Actions → Run workflow (Batched) → Chạy từng batch!**
