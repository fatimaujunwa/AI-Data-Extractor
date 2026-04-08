import anthropic
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ─────────────────────────────────────────
# CORE EXTRACTION FUNCTION
# ─────────────────────────────────────────
def extract_data(raw_text):
    prompt = f"""You are a data extraction AI. Your job is to extract structured data from messy unstructured text.

Extract the following fields from the text below and return ONLY a valid JSON object. Nothing else. No explanation. Just the JSON.

Fields to extract:
- name: (first name only)
- location: (city or region)
- email: (email address if mentioned, otherwise "not provided")
- customer_since: (year if mentioned, otherwise "unknown")
- issue_type: (Billing / Technical / Feature Request / Complaint / Upgrade / Positive Feedback)
- sentiment: (Positive / Negative / Neutral)
- priority: (High / Medium / Low) based on urgency
- summary: (one sentence summary of the situation)
- suggested_action: (one sentence on what the team should do next)

Raw Text:
{raw_text}

Return ONLY the JSON object. No markdown. No explanation."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse the JSON response from Claude
    response_text = message.content[0].text.strip()
    extracted = json.loads(response_text)
    return extracted

# ─────────────────────────────────────────
# PROCESS ALL RECORDS
# ─────────────────────────────────────────
def process_records(filepath):
    print("📂 Loading sample data...")
    
    with open(filepath, "r") as f:
        content = f.read()
    
    # Split by record marker
    records = [r.strip() for r in content.split("---RECORD") if r.strip()]
    records = [r.split("---\n", 1)[-1].strip() for r in records]
    
    print(f"✅ Found {len(records)} records to process\n")
    
    results = []
    
    for i, record in enumerate(records, 1):
        print(f"🔄 Extracting data from Record {i}...")
        try:
            extracted = extract_data(record)
            extracted["record_id"] = i
            results.append(extracted)
            print(f"✅ Record {i} extracted successfully")
        except Exception as e:
            print(f"❌ Record {i} failed: {e}")
    
    return results

# ─────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────
def display_results(results):
    print("\n" + "="*60)
    print("📊 EXTRACTION RESULTS")
    print("="*60)
    
    for r in results:
        print(f"\n🔹 RECORD {r['record_id']}")
        print(f"   Name:           {r.get('name', 'N/A')}")
        print(f"   Location:       {r.get('location', 'N/A')}")
        print(f"   Email:          {r.get('email', 'N/A')}")
        print(f"   Customer Since: {r.get('customer_since', 'N/A')}")
        print(f"   Issue Type:     {r.get('issue_type', 'N/A')}")
        print(f"   Sentiment:      {r.get('sentiment', 'N/A')}")
        print(f"   Priority:       {r.get('priority', 'N/A')}")
        print(f"   Summary:        {r.get('summary', 'N/A')}")
        print(f"   Action:         {r.get('suggested_action', 'N/A')}")
        print("-"*60)

# ─────────────────────────────────────────
# SAVE RESULTS
# ─────────────────────────────────────────
def save_results(results):
    # Save as JSON
    json_filename = f"extracted_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(json_filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 JSON report saved as {json_filename}")
    
    # Save as readable report
    txt_filename = f"extracted_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(txt_filename, "w") as f:
        f.write("AI DATA EXTRACTOR REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("="*60 + "\n\n")
        
        # Priority summary
        high = [r for r in results if r.get('priority') == 'High']
        medium = [r for r in results if r.get('priority') == 'Medium']
        low = [r for r in results if r.get('priority') == 'Low']
        
        f.write("PRIORITY SUMMARY\n")
        f.write("-"*40 + "\n")
        f.write(f"🔴 High Priority:   {len(high)} records\n")
        f.write(f"🟡 Medium Priority: {len(medium)} records\n")
        f.write(f"🟢 Low Priority:    {len(low)} records\n\n")
        
        # Sentiment summary
        negative = [r for r in results if r.get('sentiment') == 'Negative']
        positive = [r for r in results if r.get('sentiment') == 'Positive']
        neutral = [r for r in results if r.get('sentiment') == 'Neutral']
        
        f.write("SENTIMENT SUMMARY\n")
        f.write("-"*40 + "\n")
        f.write(f"😡 Negative: {len(negative)} records\n")
        f.write(f"😊 Positive: {len(positive)} records\n")
        f.write(f"😐 Neutral:  {len(neutral)} records\n\n")
        
        # Individual records
        f.write("DETAILED RECORDS\n")
        f.write("-"*40 + "\n")
        for r in results:
            f.write(f"\nRecord {r['record_id']}: {r.get('name')} - {r.get('issue_type')} ({r.get('priority')} Priority)\n")
            f.write(f"Summary: {r.get('summary')}\n")
            f.write(f"Action: {r.get('suggested_action')}\n")
    
    print(f"📄 Text report saved as {txt_filename}")

# ─────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────
def run_extractor():
    print("🚀 AI DATA EXTRACTOR")
    print("="*60)
    print("Transforms messy unstructured text into clean structured data")
    print("="*60)
    
    # Process all records from sample file
    results = process_records("sample_data.txt")
    
    # Display in terminal
    display_results(results)
    
    # Save outputs
    save_results(results)
    
    print("\n" + "="*60)
    print("✅ EXTRACTION COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    run_extractor()