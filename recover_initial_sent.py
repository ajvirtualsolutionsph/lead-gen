from sheets import get_worksheet, TAB_INITIAL_SENT

rows = [
    # 05/15 batch — followup drafts lost, need re-draft before 05/17
    {"business_name": "Precise Plumbing", "email": "info@preciseplumbingmo.com", "category": "Plumbing", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29aeffef85c21"},
    {"business_name": "Paschal Air, Plumbing & Electric", "email": "info@gopaschal.com", "category": "Plumbing", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af01ddcc1df"},
    {"business_name": "Chris Downing 117 Service", "email": "contact@cd117service.com", "category": "Plumbing", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af03707bce2"},
    {"business_name": "Black Sheep", "email": "MIKE@FLAMESTEAKHOUSE.COM", "category": "Restaurant", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af0464e66e0"},
    {"business_name": "Civil Kitchen", "email": "civilsgf@gmail.com", "category": "Restaurant", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af06c12cc12"},
    {"business_name": "Flame Steakhouse", "email": "matt@flamesteakhouse.com", "category": "Restaurant", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af089f68f13"},
    {"business_name": "OXO Bar & Grill", "email": "oxobarandgrill@gmail.com", "category": "Restaurant", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af0b362efdc"},
    {"business_name": "Ariake Sushi & Robata", "email": "doj632@hotmail.com", "category": "Restaurant", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af0c270a3b4"},
    {"business_name": "Farmers Gastropub", "email": "info@farmersgastropub.com", "category": "Restaurant", "sent": "2026-05-15 11:29", "status": "Initial Sent", "thread_id": "19e29af0ec8e7c2f"},
    {"business_name": "Downtown Pizza & Sports Bar", "email": "downtownpizzasportsbar@gmail.com", "category": "Restaurant", "sent": "2026-05-15 11:30", "status": "Initial Sent", "thread_id": "19e29af10caf84e6"},
    # 05/16 batch — followup drafts recovered from session output
    {
        "business_name": "The Antler Room", "email": "hello@theantlerroomkc.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e308744fec019b",
        "followup": (
            "Just wanted to bump this up in case it got buried. For a place rotating menus as often as "
            "The Antler Room does, keeping social content and inquiry replies consistent manually is a "
            "real time drain — and it compounds fast.\n\nHappy to walk you through what that looks like "
            "automated — 30 minutes is all it takes.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "Anjin", "email": "info@anjinkc.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e308749f4b3b8d",
        "followup": (
            "Wanted to follow up quickly on my last note about Anjin. For a restaurant running at your "
            "pace — packed reservations, weekend rushes, a menu people can't stop writing about — the "
            "repetitive inbox and posting work adds up fast. Happy to walk you through what this looks "
            "like in practice.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "The Wise Guy", "email": "INFO@THEWISEGUYKC.COM",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e30874c0418982",
        "followup": (
            "Just wanted to bump this up in case it got buried. If The Wise Guy is managing its own "
            "content, promos, and inquiry follow-ups manually right now, that's probably the most "
            "expensive part of the week — just in time, not dollars.\n\nHappy to walk you through a "
            "quick demo if it's useful.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "Lula Southern Cookhouse", "email": "kravinitkc@gmail.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e30874f4ddfaa6",
        "followup": (
            "Lula's fried chicken reputation is doing a lot of heavy lifting — but if reservations are "
            "still being managed manually, you're likely leaving bookings on the table every week.\n\n"
            "I put together a few ideas specific to Lula that I'd love to walk through. Would a quick "
            "30 minutes make sense?\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "Clay & Fire", "email": "ClayandFirekc@gmail.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e30875076d2fa5",
        "followup": (
            "Hey — just wanted to circle back on my note from last week.\n\nIf you're still fielding "
            "the same reservation questions and manually posting your weekly specials, those are exactly "
            "the tasks I'd automate first for Clay & Fire.\n\nHappy to show you what that looks like in "
            "practice — no pressure, just a quick look.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "The Farmhouse", "email": "nikki@thefarmhousekc.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e30875250ecf5e",
        "followup": (
            "The Farmhouse's seasonal menu and venue side are exactly the kind of operation where a few "
            "smart automations make a real dent — event inquiry replies, brunch promo scheduling, content "
            "that goes out without anyone touching it manually.\n\nWorth 30 minutes to see what that "
            "looks like?\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "Mason Jar", "email": "foh@masonjarkc.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e308755e2e2407",
        "followup": (
            "Terri, just wanted to make sure this didn't get buried. With private event inquiries and "
            "weekly specials to manage on top of running front of house, Mason Jar is exactly the kind "
            "of operation where automation pays for itself fast.\n\nHappy to walk you through it in 30 "
            "minutes.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "1930 Classic Kitchen", "email": "info@1930classickitchen.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e3087571445270",
        "followup": (
            "Still thinking about it? Wanted to share one specific thing: I can build a system that "
            "automatically responds to every catering inquiry with a personalized draft — routed to your "
            "inbox for one-click approval before anything goes out. No missed leads, no manual "
            "back-and-forth.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "Naree Kitchen", "email": "nareerat0131@yahoo.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e308759dc018bb",
        "followup": (
            "Naree Kitchen's reputation across 173 reviews says the food and hospitality are already "
            "there — the part that usually slips is the marketing consistency behind the scenes. If "
            "you're still posting promos manually or letting DMs pile up, that's the first thing worth "
            "fixing. Happy to walk you through it in 30 minutes.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
    {
        "business_name": "Holy Smoke BBQ", "email": "holysmokebbqkc@gmail.com",
        "category": "Restaurant", "sent": "2026-05-16 19:23", "status": "Initial Sent",
        "thread_id": "19e30875bca47002",
        "followup": (
            "Hey — just wanted to follow up on my last note. Holy Smoke selling out daily is a strong "
            "signal there's more demand to capture — the right automation can help you stay visible on "
            "the days people are deciding where to eat. Happy to walk you through it if the timing works "
            "better now.\n\nhttps://calendly.com/aj-virtualsolutionsph/30min"
            "\n\nBook a 30-min demo — I'll show you exactly where you're losing time and how to get it back."
        ),
    },
]

ws = get_worksheet(TAB_INITIAL_SENT)
headers = ws.row_values(1)

for row in rows:
    ws.append_row([row.get(col, "") for col in headers], value_input_option="RAW")
    print(f"[OK] {row['business_name']}")

print(f"\nDone. {len(rows)} rows re-inserted.")
