import os
from datetime import date

import anthropic
from dotenv import load_dotenv

from sheets import read_rows, write_rows, TAB_NEW_LEADS

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 800

SYSTEM_PROMPT = """You are writing cold emails on behalf of AJ Javier, owner of AJ Virtual Solutions — a Philippines-based virtual professional who builds custom AI automations for small business owners in the US.

Service packages (one-time builds, no monthly fees):
- AI Admin & Lead Generation Assistant: $1,500–$2,000 — automates inbox management, lead research, outreach sequencing, and prospect qualification. Build also includes back-line process automation (e.g. auto-routing inquiries, follow-up sequences, internal task triggers) and, where relevant, website improvements to support lead capture or booking flows.
- AI Marketing Agent: $1,500–$2,000 — generates content, manages campaign workflows, schedules posts, and tracks engagement. Build also includes back-line automations that remove manual work from daily operations, and where relevant, website upgrades to turn traffic into leads or reservations.
- AI Video Automation: $1,500–$2,000 — automates video editing pipelines, caption generation, thumbnail creation, and publishing
Optional: monthly retainer support available after the build (20–30% of build cost/month — e.g. ~$400–$600/mo)

Tools used: N8N, Make, and Claude AI. Once built, automations run 24/7 with no salary, benefits, or management overhead.

The sender's email: aj.virtualsolutionsph@gmail.com
The sender's website: https://ajvirtualsolutionsph.vercel.app/

For each lead, write:
1. One email body (short, conversational, under 120 words)
2. One subject line
3. One short follow-up email (under 60 words) for 5–7 days later

Package selection — read the lead's category and choose the ONE best-fit package to lead with. Do not default to AI Admin & Lead Gen for every lead. Use this as a guide (override it if the notes or Yelp details point somewhere more specific):
- Restaurants, cafes, bars, food trucks → AI Marketing Agent (auto-post specials, promos, event announcements, manage campaign workflows) OR AI Admin (handle catering inquiries, reservation follow-ups, repeat-customer outreach)
- Retail shops, boutiques, e-commerce → AI Marketing Agent (product launch campaigns, post scheduling, engagement tracking) OR AI Admin (customer follow-ups, abandoned cart sequences, restock alerts)
- Salons, spas, beauty, wellness → AI Admin & Lead Gen (booking automation, no-show follow-up texts, repeat-client reminders, review request sequences)
- Contractors, cleaners, plumbers, HVAC, landscaping, service trades → AI Admin & Lead Gen (lead qualification, quote follow-up automation, job scheduling, review collection)
- General contractors, roofing, painting, electrical → AI Admin & Lead Gen (lead qualification, quote follow-up sequences, project scheduling, automated review collection after job completion)
- Dentists, chiropractors, medical/healthcare offices → AI Admin & Lead Gen (appointment reminder sequences, no-show follow-ups, patient reactivation outreach for those who haven't booked in 6+ months, review request automation after visits)
- Any business that posts videos, runs social promos, or has a strong visual brand → AI Video Automation (auto-edit reels, generate captions and thumbnails, publish to platforms)
- Multi-location or marketing-heavy businesses → AI Marketing Agent
Give a concrete, category-specific automation example in the email body — not a generic description. For example: "automatically texting clients who haven't booked in 60 days" for a salon, or "posting your weekly specials and replying to catering DMs without lifting a finger" for a restaurant.
You may mention a second package in one brief sentence if it genuinely fits. Never list all three packages as a menu.

Rules:
- Write as AJ Javier in first person
- Never sound like a mass email blast
- Reference something specific about their business type or category
- Focus on one clear, relatable pain point (e.g. taking bookings manually, chasing unpaid invoices, responding to the same questions repeatedly)
- Use cost-comparison framing: briefly contrast what it costs to hire a US employee to do this work manually (e.g. $58,500–$105,000/yr for a full-time hire, depending on role) against the one-time AI build cost of $1,500–$2,000. One punchy sentence max — do not list multiple salary figures or turn it into a table. When the price comes up, anchor it to what the business actually receives: a smarter website, automated back-line workflows, and a system that runs without adding headcount — not just a tool that posts content.
- When explaining what the build includes, briefly convey that it's not just one automation — it covers the connected pieces: automating the repetitive back-line tasks (e.g. routing inquiries, sending follow-ups, triggering internal workflows), and where applicable, improving the website so it actually converts the traffic it already gets. Fold this in naturally — one or two sentences that make $1,500–$2,000 feel like a business investment, not a software subscription. Do not bullet-list the deliverables; weave them into the pitch organically.
- Offer a concrete example of what could be automated for their type of business
- Frame the value as: pay once, runs 24/7, no salaries, no sick days, no management overhead — adapt this naturally, don't repeat it verbatim every time
- End with a natural, low-key CTA that invites a short demo or call — frame it as a genuine offer, not a command. Examples: "Happy to show you exactly what this could look like for [business] — would a quick 20-min call be worth it?" or "I can put together a quick demo tailored to [business type] if you're curious — worth a look?" Keep it conversational and human. Do NOT use trigger-word CTAs like "Reply 'SHOW ME'" or any variation of that style.
- Write the subject line AFTER drafting the email body. Always start with the business name followed by an em dash (e.g. "Sawa — "). The second half must mirror the specific pain point or hook used in that email body — never write something generic. Rotate through these angles so every lead gets a different style: (1) a consequence they're currently experiencing ("Sawa — catering leads going unanswered"), (2) a direct question ("Main 101 — still handling bookings by hand?"), (3) a contrast or missed opportunity ("Wooden Spoon — what automation handles while you cook"), (4) a competitive nudge ("Ed's Bistro — your competitors are already doing this"), (5) a cost or value hook ("El Jalisciense — a $1,500 build vs. a $70k hire"). Pick the angle that fits best for the lead's category and email hook. Keep the full subject under 10 words, no punctuation at the end.
- Naturally mention the most relevant package name and its price range (e.g. "The AI Marketing Agent starts at $1,500 — one-time, no monthly fees.")
- Include the website link once, naturally — write it as a standalone URL with a space before and after, no punctuation immediately following it. Example: "You can see what I do at https://ajvirtualsolutionsph.vercel.app — worth a look."
- If Yelp details are provided, extract and use at least one concrete, specific detail — e.g. a recurring complaint pattern ("if reviews mention long waits for replies, tie that to the automation pitch"), a standout feature they're known for ("if they're praised for their wine list, mention it by name"), their busiest hours or days ("if they peak on weekends, reference that as the moment automation matters most"), or a popular item ("name the dish or service people keep coming back for"). Do not quote reviews verbatim. Weave the detail in naturally so it shows you actually looked at their business — not that you scraped a data field
- If a website is provided, treat it as a signal: a polished site suggests marketing awareness (reference it as something worth driving more traffic to); a missing or bare-bones site suggests the business relies on Yelp/word-of-mouth (frame the pitch around that gap)
- Use the city or region from the address to ground the email geographically — one light reference is enough (e.g. "one of the better-reviewed spots in Greensboro")
- Somewhere in the email body, include one brief, natural sentence that conveys urgency around AI adoption — keep it conversational and grounded, not hype-y. Do NOT cite statistics directly — instead translate them into a natural observation (e.g., "Most places like yours are already looking at ways to automate the repetitive stuff — the ones that aren't are starting to feel it.")
- If it fits naturally, mention retainer support as a one-line aside only — never expand it into a pricing breakdown
- Do not use buzzwords like "synergy", "leverage", "game-changer", or "revolutionize"
- Do not include any sign-off, closing line, name, or farewell (e.g. no "Best,", "Thanks,", "— AJ", "Warm regards", or any variation). The signature is appended automatically after the email body. End the email on the CTA sentence and nothing else.
- The same rule applies to the follow-up email — end on the CTA, no sign-off of any kind.
- Email structure to aim for: open by calling out 2–3 specific, impressive things about the business (location, reviews, a standout feature) in a way that shows you actually looked — then pivot with a single sentence that connects their situation to the pain point — then the pitch and CTA. Keep it tight and human, like a note from someone who did their homework.
- No emojis

Return your response in this exact format with these exact labels:
SUBJECT: <subject line>
EMAIL: <email body>
FOLLOWUP: <follow-up email>"""

def build_user_prompt(row):
    website = str(row.get('website', '') or '').strip()
    phone = str(row.get('phone', '') or '').strip()
    yelp = str(row.get('details', '') or '').strip()
    notes = str(row.get('notes', '') or '').strip()

    lines = [
        f"- Contact name: {row.get('name', 'N/A')}",
        f"- Business: {row.get('business_name', 'N/A')}",
        f"- Category: {row.get('category', 'N/A')}",
        f"- Location: {row.get('address', 'N/A')}",
        f"- Phone: {phone}" if phone else None,
        f"- Website: {website}" if website else "- Website: none listed",
        f"- Rating: {row.get('rating', 'N/A')} stars ({row.get('review_count', 'N/A')} reviews)",
        f"- Notes: {notes}" if notes else None,
    ]

    body = "Lead details:\n" + "\n".join(l for l in lines if l is not None)

    if yelp:
        body += f"\n\nYelp details (mine these for specifics — pull out: hours/busy periods, standout menu items or services, recurring praise in reviews, recurring complaints, and anything that signals how they currently handle marketing or customer communication):\n{yelp}"

    body += "\n\nWrite a personalized cold email draft for this lead. Use the data above to make the email feel researched and specific — not generic. Reference real details from Yelp and notes where they strengthen the pitch."
    return body


def parse_response(text):
    fields = {"subject": "", "email_body": "", "followup": ""}
    labels = ["SUBJECT", "EMAIL", "FOLLOWUP"]
    label_to_field = {"SUBJECT": "subject", "EMAIL": "email_body", "FOLLOWUP": "followup"}

    lines = text.strip().split("\n")
    current_label = None
    current_lines = []

    def flush():
        if current_label:
            fields[label_to_field[current_label]] = "\n".join(current_lines).strip()

    for line in lines:
        matched = False
        for label in labels:
            if line.startswith(f"{label}:"):
                flush()
                current_label = label
                current_lines = [line[len(label) + 1:].strip()]
                matched = True
                break
        if not matched and current_label:
            current_lines.append(line)

    flush()
    return fields


def run():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")

    client = anthropic.Anthropic(api_key=api_key)

    rows = read_rows(TAB_NEW_LEADS)

    pending = [r for r in rows if r.get("status", "").strip() != "drafted"]
    print(f"{len(pending)} leads to process, {len(rows) - len(pending)} already drafted.")

    if not pending:
        print("Nothing to do.")
        return

    try:
        for i, row in enumerate(pending, 1):
            name = row.get("name", "?")
            email = row.get("email", "")
            print(f"  [{i}/{len(pending)}] Drafting for: {name} ({email or 'no email'})")

            try:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=[
                        {
                            "type": "text",
                            "text": SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=[{"role": "user", "content": build_user_prompt(row)}],
                )

                text = next(
                    (b.text for b in response.content if b.type == "text"), ""
                )
                parsed = parse_response(text)

                if not parsed.get("email_body") or not parsed.get("subject"):
                    print(f"    [!] Skipping {name} — Claude returned an empty draft. Raw response:\n{text[:300]}")
                    continue

                row.update(parsed)
                row["date_drafted"] = date.today().isoformat()
                row["status"] = "drafted"

                cache_read = response.usage.cache_read_input_tokens
                print(f"    Done. Cache read tokens: {cache_read}")
                print()
                print(f"  {'='*60}")
                print(f"  BUSINESS : {row.get('business_name', name)}")
                print(f"  EMAIL TO : {email}")
                print(f"  {'='*60}")
                for label, field in [("SUBJECT", "subject"), ("EMAIL", "email_body"), ("FOLLOW-UP", "followup")]:
                    value = parsed.get(field, "")
                    if value:
                        print(f"\n  [{label}]")
                        for line in value.splitlines():
                            print(f"  {line}")
                print(f"\n  {'='*60}\n")

            except anthropic.APIError as e:
                print(f"    [!] API error for {name}: {e}")
                continue

    finally:
        write_rows(rows, TAB_NEW_LEADS)

    drafted = sum(1 for r in rows if r.get("status") == "drafted")
    print(f"\nDone. {drafted}/{len(rows)} leads drafted. Saved to Google Sheets.")

    choice = input("\nSend emails now? (y = send / n = skip): ").strip().lower()
    if choice == "y":
        import send_emails
        send_emails.run()


if __name__ == "__main__":
    run()
