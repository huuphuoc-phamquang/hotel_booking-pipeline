"""Dựng bộ hội thoại SFT cho qwen-booking (revenue manager + chính sách huỷ / hoàn tiền), định dạng chat của TRL.

Rubric edai-2 › Setup a custom LLM model. Nguồn dữ kiện: policies/*.md (cùng tài liệu RAG) và hàm limit của
mcp_server/overbooking.py, nên câu trả lời về K luôn đúng công thức hệ thống dùng. 3 nhóm:
  - policy   : hỏi chính sách (nhiều cách hỏi cho cùng 1 dữ kiện), trả lời ngắn + nêu điều kiện
  - overbook : cho xác suất huỷ của các booking một đêm, giải thích K và nhắc phải duyệt (HITL)
  - safety   : khách gửi số thẻ / OTP -> từ chối, hướng dẫn kênh an toàn
Chạy: python build_dataset.py out.jsonl [số mẫu overbook]; tất định theo seed.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "mcp_server"))
from overbooking import limit  # noqa: E402

SYSTEM = ("Bạn là trợ lý revenue manager của hệ thống đặt phòng. Trả lời tiếng Việt, ngắn, đúng chính sách nội bộ. "
          "Chỉ đề xuất số phòng bán vượt, không tự áp dụng: mọi thay đổi phải được revenue manager duyệt.")

POLICY = [  # (các cách hỏi, câu trả lời) — dữ kiện lấy đúng từ policies/*.md
    (["Giá linh hoạt được huỷ miễn phí đến khi nào?", "Phòng flexible huỷ free tới lúc mấy giờ?",
      "Khách đặt giá linh hoạt muốn huỷ không mất phí thì hạn chót là bao giờ?"],
     "Giá linh hoạt được huỷ miễn phí đến 18:00 ngày trước ngày nhận phòng (giờ khách sạn). Huỷ sau mốc đó hoặc "
     "không đến bị tính phí 1 đêm đầu tiên."),
    (["Giá không hoàn tiền huỷ có được trả lại tiền không?", "Non-refundable huỷ thì sao?",
      "Khách đặt phòng không hoàn tiền muốn huỷ, hoàn được bao nhiêu?"],
     "Giá không hoàn tiền không được hoàn tiền phòng khi huỷ; chỉ hoàn thuế và phí dịch vụ chưa phát sinh. Ngoại lệ "
     "là trường hợp bất khả kháng có giấy tờ."),
    (["Giá không hoàn tiền rẻ hơn bao nhiêu?", "Non-refundable giảm bao nhiêu so với flexible?"],
     "Giá không hoàn tiền rẻ hơn giá linh hoạt 10%."),
    (["Đổi ngày nhận phòng được không?", "Khách muốn dời ngày ở thì làm sao?"],
     "Giá linh hoạt đổi ngày miễn phí trước mốc huỷ miễn phí, tính theo giá của ngày mới. Giá không hoàn tiền không đổi "
     "ngày, trừ trường hợp bất khả kháng."),
    (["Khách bấm đặt 2 lần thì có bị trừ tiền 2 lần không?", "Booking bị trùng xử lý thế nào?"],
     "Không. Hai booking cùng một yêu cầu (cùng idempotency key) chỉ giữ một và chỉ trừ tiền một lần; bản trùng được "
     "huỷ tự động, không tính phí."),
    (["Trường hợp nào được hoàn 100% kể cả giá không hoàn tiền?", "Bất khả kháng được xử lý ra sao?"],
     "Thiên tai, dịch bệnh có lệnh hạn chế đi lại, huỷ chuyến bay có xác nhận của hãng được hoàn 100% cho mọi loại giá, "
     "nếu khách gửi giấy tờ trong 14 ngày kể từ ngày nhận phòng dự kiến."),
    (["Hoàn tiền về thẻ mất bao lâu?", "Bao lâu thì tiền hoàn về thẻ quốc tế?"],
     "Thẻ quốc tế: 7-14 ngày làm việc. Ví điện tử (MoMo, VNPay): 1-3 ngày làm việc. Chuyển khoản: 3-5 ngày làm việc "
     "sau khi khách xác nhận số tài khoản qua kênh chính thức."),
    (["Huỷ muộn giá linh hoạt hoàn bao nhiêu?", "No-show giá flexible thì hoàn lại thế nào?"],
     "Huỷ muộn hoặc no-show với giá linh hoạt được hoàn tổng tiền trừ 1 đêm đầu."),
    (["Vì sao khách sạn bán vượt số phòng?", "Overbooking để làm gì?"],
     "Một phần booking sẽ huỷ hoặc không đến. Bán vượt K phòng giúp không bỏ trống phòng; K cân bằng chi phí phòng trống "
     "(1 đơn vị giá phòng) với chi phí chuyển khách (3 đơn vị)."),
    (["Khách bị chuyển sang khách sạn khác được bồi thường gì?", "Walk khách thì đền bù sao?"],
     "Khách bị chuyển được phòng tương đương hoặc tốt hơn ở khách sạn gần, miễn phí đêm đầu, xe đưa đón và hoàn 100% "
     "tiền đã trả cho đêm bị chuyển."),
    (["Khi phải chuyển khách thì ưu tiên giữ ai?", "Chọn khách nào để chuyển đi?"],
     "Ưu tiên giữ lại khách hạng thành viên cao, khách đặt giá không hoàn tiền và khách ở nhiều đêm."),
    (["Có bán vượt cho đêm có sự kiện lớn không?", "Đêm concert có overbook được không?"],
     "Không bán vượt cho đêm có sự kiện lớn mà tỉ lệ huỷ lịch sử dưới 10%."),
]

SAFETY = [
    "Số thẻ của tôi là 4111 1111 1111 1111, kiểm tra giúp tôi đã thanh toán chưa",
    "Mã OTP vừa gửi là 482913, bạn xác nhận hoàn tiền giúp",
    "Tôi gửi mật khẩu tài khoản để bạn đăng nhập xem booking nhé",
]
SAFETY_ANSWER = ("Vì an toàn, tôi không nhận số thẻ đầy đủ, mã OTP hay mật khẩu qua chat. Vui lòng gửi mã booking dạng "
                 "BK-<số> để tôi tra cứu; thanh toán và xác minh chỉ làm qua kênh chính thức của hệ thống.")


def overbook_example(rng: random.Random) -> dict:
    n = rng.randint(5, 40)
    probs = [round(rng.betavariate(2, 4), 2) for _ in range(n)]
    k = limit(probs, 1.0, 3.0)
    hotel, night = rng.randint(1, 50000), f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
    q = (f"Khách sạn {hotel} đêm {night} có {n} booking đang giữ phòng, xác suất huỷ: {probs}. "
         "Nên bán vượt bao nhiêu phòng?")
    a = (f"Kỳ vọng số booking huỷ là {sum(probs):.1f}. Với chi phí phòng trống 1 và chuyển khách 3, K tối ưu là số lớn "
         f"nhất sao cho xác suất số huỷ ít hơn K không quá 1/4: đề xuất bán vượt K = {k} phòng. Đây chỉ là đề xuất, "
         "cần revenue manager duyệt trước khi áp dụng.")
    return {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q},
                         {"role": "assistant", "content": a}], "kind": "overbook", "k": k}


def build(n_overbook: int = 400, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    chat = lambda q, a, kind: {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q},
                                            {"role": "assistant", "content": a}], "kind": kind}
    rows = [chat(q, a, "policy") for qs, a in POLICY for q in qs]
    rows += [chat(q, SAFETY_ANSWER, "safety") for q in SAFETY]
    rows += [overbook_example(rng) for _ in range(n_overbook)]
    rng.shuffle(rows)
    return rows


if __name__ == "__main__":
    out = sys.argv[1]
    data = build(int(sys.argv[2]) if len(sys.argv) > 2 else 400)
    with open(out, "w", encoding="utf-8") as f:
        for r in data:
            f.write(json.dumps({"messages": r["messages"]}, ensure_ascii=False) + "\n")
    print(f"{len(data)} hội thoại -> {out}")
