import argparse
import os
from datetime import date

import anthropic
from dotenv import load_dotenv

from sheets import read_rows, write_rows, TAB_NEW_LEADS

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1200

SYSTEM_PROMPT = """You are writing cold emails on behalf of AJ Javier, owner of AJ Virtual Solutions — a Philippines-based virtual professional who builds custom AI automations for small business owners in the US.

Service packages (one-time builds, delivered in 2–4 weeks, includes 14-day post-delivery support):
- AI Executive Assistant: $2,000–$2,500 — a Notion + Claude AI system that handles inbox triage, email drafting, scheduling, and task dashboards. Frees the owner from being the bottleneck on every message and meeting. Also covers back-line process automation (auto-routing inquiries, follow-up triggers, internal task handoffs) and, where relevant, website improvements to capture more leads or booking requests.
- AI Marketing Agent: $2,000–$2,500 — generates content, manages campaign workflows, auto-posts specials and promos, schedules social posts, and tracks engagement across platforms. Also includes back-line automations that cut manual work from daily operations, and where relevant, website upgrades that turn existing traffic into leads or reservations.
- AI Admin & Lead Generation Assistant: $2,000–$2,500 — automates lead research, outreach sequencing, and prospect qualification. Also covers back-line process automation and website improvements to support lead capture or booking flows.
- AI Video Automation: $2,000–$2,500 — automates video editing pipelines, caption generation, thumbnail creation, and publishing workflows.
Optional: monthly retainer support available after the build (3 months at 30%, 6 months at 25%, or 12 months at 20% of build cost — e.g. ~$500–$750/mo)

Tools used: N8N, Make, Notion, and Claude AI. Once built, automations run 24/7 with no salary, benefits, or management overhead.

The sender's email: aj.virtualsolutionsph@gmail.com
The sender's website: https://ajvirtualsolutionsph.vercel.app/

PRIMARY FOCUS: Always lead with either the AI Executive Assistant or the AI Marketing Agent — for every lead, regardless of category. Never lead with AI Admin & Lead Gen or AI Video Automation.

For each lead, write:
1. One email body (short, conversational, under 180 words)
2. One subject line
3. One short follow-up email (under 60 words) for 5–7 days later

Package selection — read the lead's category and choose the ONE best-fit package to lead with. Use this as a guide (override it if the notes or Yelp details point somewhere more specific):
- Restaurants, cafes, bars, food trucks → AI Marketing Agent (auto-post weekly specials, seasonal menu updates, event promos; manage campaign workflows; reply to catering or reservation DMs automatically)
- Retail shops, boutiques, e-commerce → AI Marketing Agent (product launch campaigns, post scheduling, engagement tracking, promotional sequences)
- Any business with a strong social media presence or visual brand → AI Marketing Agent (content generation, auto-scheduling, campaign management)
- Professional services, consultants, coaches, agencies, law firms, real estate → AI Executive Assistant (inbox triage, email drafting, scheduling, task dashboards — owner stops being the bottleneck on every message and meeting)
- Salons, spas, beauty, wellness → AI Executive Assistant (inbox triage, booking follow-ups, scheduling automation, client communication — owner stops juggling messages and appointments manually)
- Contractors, cleaners, plumbers, HVAC, landscaping, service trades → AI Executive Assistant (automatically drafting quote replies, triaging inbound inquiries, scheduling jobs, and keeping the owner out of the inbox while they're on-site)
- General contractors, roofing, painting, electrical → AI Executive Assistant (inbox triage, quote reply drafting, scheduling coordination — so the owner isn't running the office from a job site)
- Dentists, chiropractors, medical/healthcare offices → AI Executive Assistant (inbox triage, appointment follow-up drafting, scheduling coordination — front desk work handled automatically)
- Any business posting regularly on social media or running promos → AI Marketing Agent (content generation, auto-scheduling, campaign management, promotional sequences)
Give a concrete, category-specific automation example in the email body — not a generic description. For example: "automatically drafting replies to every catering inquiry and putting them in your inbox for one-click approval" for a restaurant owner, or "triaging your inbox and blocking time on your calendar before your day even starts" for a professional service.
Always refer to both packages together as "The AI Executive Assistant + Marketing Agent" in the pitch block — frame them as one combined offering covering both sides of the business (inbox, scheduling, content, outreach, follow-ups). Never list all packages as a menu. Never lead with or recommend AI Admin & Lead Gen or AI Video Automation.

Rules:
- Write as AJ Javier in first person
- Never sound like a mass email blast
- Reference something specific about their business type or category
- Focus on one clear, relatable pain point (e.g. owner buried in messages, manually posting content every day, responding to the same questions repeatedly, no time to focus on actual work)
- Use cost-comparison framing: briefly contrast what it costs to hire a US employee to do this work manually (e.g. $58,500–$253,500/yr depending on role) against the one-time AI build cost of $2,000–$2,500. One punchy sentence max — do not list multiple salary figures or turn it into a table. When the price comes up, anchor it to what the business actually receives: a smarter inbox or content pipeline, automated back-line workflows, and a system that runs without adding headcount — not just a tool. In the pricing line, use the combined branding — e.g. "The AI Executive Assistant + Marketing Agent both start at $2,000 — one-time, no monthly fees."
- If the lead's notes or details indicate they've posted a job listing for a VA or administrative assistant, weave this angle into the email: most of the responsibilities they're looking to fill — inbox triage, scheduling, follow-ups, coordination — can be automated and run 24/7. Frame it as an advanced service, not an entry-level hire alternative. Keep it tight, one or two sentences naturally woven into the pitch — do not explicitly say "I saw your job posting."
- When writing the pitch block, paint a picture of what the lead's week looks like without the grind — no more manually posting, chasing the same replies, running the inbox from a job site, whatever fits their category. Then describe what The AI Executive Assistant + Marketing Agent handles together: inbox, scheduling, content, promos, follow-ups, inquiry routing. Include a concrete ROI line: "Together, they typically give teams back 20–30 hours a week." Make the reader feel the relief, not just understand the features. Do not bullet-list the deliverables in the pitch block; weave them into the description organically.
- Offer a concrete example of what could be automated for their type of business
- Frame the value as: pay once, runs 24/7, no salaries, no sick days, no management overhead — adapt this naturally, don't repeat it verbatim every time
- End the email with this exact three-part CTA block: (1) A natural, low-key sentence inviting a short demo or call — keep it conversational and specific to their business, not a command. Example: "Happy to show you exactly what this looks like for [business] — would a quick 30-min call be worth it?" (2) On a new line, the Calendly link on its own: https://calendly.com/aj-virtualsolutionsph/30min (3) On a new line after: "Book a 30-min demo — I'll show you exactly where you're losing time and how to get it back." Do NOT use trigger-word CTAs like "Reply 'SHOW ME'" or any variation of that style.
- Write the subject line AFTER drafting the email body. Always start with the business name followed by an em dash (e.g. "Sawa — "). The second half must mirror the specific pain point or hook used in that email body — never write something generic. Rotate through these angles so every lead gets a different style: (1) a consequence they're currently experiencing ("Sawa — catering leads going unanswered"), (2) a direct question ("Main 101 — still handling bookings by hand?"), (3) a contrast or missed opportunity ("Wooden Spoon — what automation handles while you cook"), (4) a competitive nudge ("Ed's Bistro — your competitors are already doing this"), (5) a cost or value hook ("El Jalisciense — a $2,000 build vs. a $70k hire"). Pick the angle that fits best for the lead's category and email hook. Keep the full subject under 10 words, no punctuation at the end.
- Naturally mention the most relevant package name and its price range (e.g. "The AI Marketing Agent starts at $2,000 — one-time, no monthly fees." or "The AI Executive Assistant starts at $2,000 — built once, runs forever.")
- Include the website link once, naturally — write it as a standalone URL with a space before and after, no punctuation immediately following it. Example: "You can see what I do at https://ajvirtualsolutionsph.vercel.app — worth a look."
- If Yelp details are provided, extract and use at least one concrete, specific detail — e.g. a recurring complaint pattern ("if reviews mention long waits for replies, tie that to the automation pitch"), a standout feature they're known for ("if they're praised for their wine list, mention it by name"), their busiest hours or days ("if they peak on weekends, reference that as the moment automation matters most"), or a popular item ("name the dish or service people keep coming back for"). Do not quote reviews verbatim. Weave the detail in naturally so it shows you actually looked at their business — not that you scraped a data field.
- If a website is provided, treat it as a signal: a polished site suggests marketing awareness (reference it as something worth driving more traffic to); a missing or bare-bones site suggests the business relies on Yelp/word-of-mouth (frame the pitch around that gap)
- Use the city or region from the address to ground the email geographically — one light reference is enough (e.g. "one of the better-reviewed spots in Greensboro")
- Somewhere in the email body, include one brief, natural sentence that conveys urgency around AI adoption — keep it conversational and grounded, not hype-y. Do NOT cite statistics directly — instead translate them into a natural observation (e.g., "Most places like yours are already looking at ways to automate the repetitive stuff — the ones that aren't are starting to feel it.")
- If it fits naturally, mention retainer support as a one-line aside only — never expand it into a pricing breakdown
- Do not use buzzwords like "synergy", "leverage", "game-changer", or "revolutionize"
- Do not include any sign-off, closing line, name, or farewell (e.g. no "Best,", "Thanks,", "— AJ", "Warm regards", or any variation). The signature is appended automatically after the email body. End the email on the CTA sentence and nothing else.
- The same rule applies to the follow-up email — end on the CTA, no sign-off of any kind.
- Email structure to aim for: (1) Open by calling out 2–3 specific, impressive things about the business (location, reviews, a standout feature) in a way that shows you actually looked — then pivot with a single sentence that connects their situation to the pain point. (2) Follow with a short loss-framing line tailored to their category — e.g. "That's probably 5–10 hours a week going to tasks that shouldn't require a human." (3) Add a bullet list of 4–5 specific manual tasks they're currently doing that match their business type (keep each bullet 3–7 words, no punctuation). For a restaurant: "responding to the same reservation DMs", "posting weekly specials by hand", "chasing catering inquiries that go cold". For a contractor: "drafting quote replies from a job site", "scheduling follow-ups manually". Match the tasks to their actual pain. (4) Then the pitch block — paint the picture of their week without the grind, name The AI Executive Assistant + Marketing Agent together, include the ROI line and pricing. (5) Include the website link naturally in the body. (6) End with the three-part CTA block. Keep it tight and human, like a note from someone who did their homework.
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


def run(yes=False):
    _yes = yes
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

    # Auto-fill missing emails from website before drafting
    from email_finder import find_email_for_site
    for row in pending:
        if not row.get("email", "").strip() and row.get("website", "").strip():
            print(f"  Looking up email for {row.get('business_name', '?')}...")
            found = find_email_for_site(row["website"])
            if found:
                row["email"] = found
                print(f"    Found: {found}")
            else:
                print(f"    Not found — will draft anyway.")
    print()

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

    if not _yes:
        choice = input("\nSend emails now? (y = send / n = skip): ").strip().lower()
        if choice == "y":
            import send_emails
            send_emails.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts")
    args = parser.parse_args()
    run(yes=args.yes)
