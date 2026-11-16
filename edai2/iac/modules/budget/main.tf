# Cảnh báo email khi chi tiêu (tính cả credit) chạm 50% / 80% / 100% ngân sách. Không tự tắt tài nguyên:
# hết tuần chạy `terraform destroy` ở envs/dev.
variable "billing_account" { type = string }
variable "project_number" { type = string }
variable "amount_usd" { type = number }

resource "google_billing_budget" "this" {
  billing_account = var.billing_account
  display_name    = "booking-coursework"
  budget_filter {
    projects               = ["projects/${var.project_number}"]
    credit_types_treatment = "EXCLUDE_ALL_CREDITS" # tính cả phần credit trial đã tiêu
  }
  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.amount_usd)
    }
  }
  dynamic "threshold_rules" {
    for_each = [0.5, 0.8, 1.0]
    content { threshold_percent = threshold_rules.value }
  }
}
