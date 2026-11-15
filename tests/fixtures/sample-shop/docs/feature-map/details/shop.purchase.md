# Mua sách

Đặt mua một sản phẩm với số lượng hợp lệ.

## Người dùng

- Khách dùng bản mẫu

## Điều kiện

- Đã đăng nhập.
- Có đủ hàng.

## Cách sử dụng

- Nhập sản phẩm.
- Nhập số lượng.
- Chọn Mua.

## Đầu vào

- Sản phẩm.
- Số lượng nguyên dương.

## Kết quả

- Mã đơn mới.
- Tồn kho giảm theo số lượng mua.

## Luồng chính

- Kiểm tra đăng nhập, số lượng và tồn kho.
- Tạo đơn mới, giảm tồn kho và trả mã đơn.

## Luồng thay thế

Source bản mẫu không mô tả nội dung này ở mức chức năng hiện tại.

## Ngoại lệ

- Chưa đăng nhập: từ chối.
- Số lượng không phải số nguyên dương: báo không hợp lệ.
- Không tìm thấy sản phẩm: báo lỗi.
- Không đủ hàng: báo lỗi.

## Xác minh

source_confirmed
Đã đối chiếu source bản mẫu; chưa quan sát ứng dụng web chạy.
