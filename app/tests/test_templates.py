from datetime import datetime

def generate_whatsapp_body(client_lang, stats, star_rating, reviewer_name, review_text, draft_text):
    current_date = datetime.now().strftime("%d %b")
    if client_lang == "ar-om":
        return (
            f"📊 *لوحة التحكم • {current_date}*\n"
            f"🔴 قيد الانتظار: {stats['pending']} | ✅ تم النشر: {stats['posted']}\n"
            f"    ⭐ *تقييم جديد ({star_rating} نجوم)*\n"
            f"    👤 *{reviewer_name}*\n"
            f"    \"{review_text}\"\n"
            f"    🤖 *الرد المقترح:*\n"
            f"    \"{draft_text}\"\n"
            f"    👇 *الإجراء:*\n"
            f"    1 : ✅ اعتماد ونشر\n"
            f"    2 : 🎲 صياغة جديدة"
        )
    else:
        return (
            f"📊 Dashboard • {current_date}\n"
            f"🔴 Pending: {stats['pending']} | ✅ Posted: {stats['posted']}\n\n"
            f"⭐ New {star_rating} Review\n"
            f"👤 {reviewer_name}\n"
            f"\"{review_text}\"\n\n"
            f"🤖 Proposed Reply: \"{draft_text}\"\n\n"
            f"👇 Action: 1 : Approve 2 : 🎲 Regenerate"
        )

def test_templates():
    stats = {"pending": 5, "posted": 10}
    reviewer_name = "Ahmed"
    review_text = "The Tea was great!"
    draft_text = "Glad you liked the Tea!"
    
    print("Testing Arabic Template:")
    ar_body = generate_whatsapp_body("ar-om", stats, 5, reviewer_name, review_text, draft_text)
    print(ar_body)
    assert "لوحة التحكم" in ar_body
    assert "قيد الانتظار: 5" in ar_body
    assert "الرد المقترح" in ar_body
    
    print("\nTesting English Template:")
    en_body = generate_whatsapp_body("en", stats, 5, reviewer_name, review_text, draft_text)
    print(en_body)
    assert "Dashboard" in en_body
    assert "Pending: 5" in en_body
    assert "Proposed Reply" in en_body
    
    print("\nAll template tests passed!")

if __name__ == "__main__":
    test_templates()
