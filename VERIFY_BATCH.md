# Script Kiểm Tra Batch Workflow

## Cách Kiểm Tra Workflow Đang Chạy Đúng Batch

### Vào GitHub Actions logs, bạn sẽ thấy:

```
===========================
BATCH 1 PROCESSING
Files per batch: 1000
===========================
Total files in dataset: 10000
This batch processes files: 1 to 1000
===========================
```

Hoặc với batch 3:

```
===========================
BATCH 3 PROCESSING
Files per batch: 1000
===========================
Total files in dataset: 10000
This batch processes files: 2001 to 3000
===========================
```

## Test Nhanh

### Test 1: Batch 1 với 100 files
```
Input:
- batch_number: 1
- files_per_batch: 100

Expected output in logs:
"This batch processes files: 1 to 100"
```

### Test 2: Batch 5 với 500 files
```
Input:
- batch_number: 5
- files_per_batch: 500

Expected output in logs:
"This batch processes files: 2001 to 2500"
Calculation: (5-1) * 500 = 2000, so files 2001-2500
```

### Test 3: Batch 10 với 1000 files
```
Input:
- batch_number: 10
- files_per_batch: 1000

Expected output in logs:
"This batch processes files: 9001 to 10000"
Calculation: (10-1) * 1000 = 9000, so files 9001-10000
```

## Cách Verify

1. **Chạy 2 batch khác nhau:**
   - Batch 1: batch_number=1, files_per_batch=100
   - Batch 2: batch_number=2, files_per_batch=100

2. **Check artifacts:**
   - Batch 1 sẽ có: `output-batch-1-job-0.zip`
   - Batch 2 sẽ có: `output-batch-2-job-0.zip`

3. **Check file names trong artifacts:**
   - Batch 1: Files có tên `20.35.1.txt`, `20.35.2.txt`, ..., `20.35.100.txt`
   - Batch 2: Files có tên `20.35.101.txt`, `20.35.102.txt`, ..., `20.35.200.txt`

4. **Check summary CSV:**
   - Batch 1: `summary-batch-1.csv` có 100 entries
   - Batch 2: `summary-batch-2.csv` có 100 entries khác

## Nếu Không Hoạt Động

Dấu hiệu batch không hoạt động đúng:
- ❌ Log không hiển thị batch number
- ❌ Tất cả batch xử lý cùng files
- ❌ Artifacts trùng lặp

Nhưng với code hiện tại, **NÓ SẼ HOẠT ĐỘNG** vì:
- ✅ Input được định nghĩa đúng
- ✅ Biến được truyền vào shell script
- ✅ Logic tính toán chính xác
- ✅ Echo logs rõ ràng
