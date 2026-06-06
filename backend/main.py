from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
import os
def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd"
        }.get(n % 10, "th")

    return f"{n}{suffix}"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176"
        "https://construction-dashboard-ashy.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "THIS IS MY EDITED BACKEND"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    print("UPLOAD HIT")

    # Save uploaded PDF
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Extract text from PDF
    extracted_text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text:
                extracted_text += text + "\n"
    with open("debug.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)
        report_type = "unknown"
    text_upper = extracted_text.upper()
    if "DAILY PROGRESS REPORT" in text_upper:
        report_type = "daily"
    elif re.search(
        r"DAILY REPORT\s*-\s*\d{1,2}\s+[A-Z]{3}",
        text_upper
    ):
        report_type = "monthly"
    print("REPORT TYPE:", report_type)
    total_labours_match = re.search(
        r"Total Labours on-site\s+(\d+)",
        extracted_text,
        re.IGNORECASE
    )
    monthly_total_labours = 0
    if total_labours_match:
        monthly_total_labours = int(
            total_labours_match.group(1)
        )
    print(
        "MONTHLY TOTAL LABOURS:",
        monthly_total_labours
    )

    # Site
    lines = [
    line.strip()
    for line in extracted_text.split("\n")
    if line.strip()
    ]
    site = "Unknown Site"
    # DAILY REPORT SITE EXTRACTION
    for i, line in enumerate(lines):
        if "DAILY PROGRESS REPORT" in line.upper():
            if i + 1 < len(lines):
                site = lines[i + 1]
            break
    # MONTHLY REPORT FALLBACK
    if site == "Unknown Site" and report_type == "monthly":
        for i, line in enumerate(lines):
            if "DAILY REPORT" in line.upper():
                if i + 1 < len(lines):
                    site = lines[i + 1].strip()
                break
    print("LINES 0-10:")
    for x in lines[:10]:
        print(repr(x))
    print("SITE FOUND:", site)

    # Contractor
    contractors = re.findall(
    r"([A-Za-z0-9& ]+?)\(Count wise\)",
    extracted_text
    )
    contractors = [
        c.strip()
        for c in contractors
        ]
    print("CONTRACTORS:")
    print(contractors)
    contractor_daily_labour = {}
    contractor_daily_skilled = {}
    contractor_daily_unskilled = {}
    contractor_labour = {}

    # Skilled Labour
    for idx, contractor in enumerate(contractors):
        vendor_match = re.search(
            rf"Vendor:\s*{re.escape(contractor)}.*?Labour \(By count\)",
            extracted_text,
            re.IGNORECASE | re.DOTALL
        )
        start = vendor_match.start() if vendor_match else -1
        current_vendor_end = start + len(f"Vendor: {contractor}")
        next_vendor = re.search(
            r"Vendor:",
            extracted_text[current_vendor_end:],
            re.IGNORECASE
        )
        print("CONTRACTOR:", contractor)
        print("START:", start)
        print(extracted_text[start:start+100])
        if next_vendor:
            print("NEXT VENDOR FOUND AT:", next_vendor.start())
            end=start + 1 + next_vendor.start()
            section=extracted_text[start:end]
        else:
            section = extracted_text[start:]
        skilled = 0
        unskilled = 0
        daily_attendance = {}
        # DAILY REPORT FORMAT
        skilled_section = re.search(
        r"Skilled Labour(.*?)Unskilled Labour",
        section,
        re.DOTALL | re.IGNORECASE
        )
        if skilled_section:
            skilled = sum(
                int(x)
                for x in re.findall(
                    r"[A-Za-z ]+\s+(\d+)",
                skilled_section.group(1)
                )
            )
        unskilled_section = re.search(
            r"Unskilled Labour(.*?)(?:\d{1,2}(?:st|nd|rd|th)\s+[A-Za-z]+\s+\d{4}|$)",
            section,
            re.DOTALL | re.IGNORECASE
        )
        if unskilled_section:
            unskilled = sum(
                int(x)
                for x in re.findall(
                    r"[A-Za-z ]+\s+(\d+)",
                    unskilled_section.group(1)
                )
            ) 
        #MONTHLY REPORT FORMAT
        if report_type == "monthly":
            skilled = 0
            unskilled = 0

            # Format 1
            mason_match = re.search(
                r"(?m)^Mason\s+(\d+)\s*P",
                section,
                re.IGNORECASE
            )
            helper_match = re.search(
                r"(?m)^Helper\s+(\d+)\s*P",
                section,
                re.IGNORECASE
            )
            if mason_match:
                skilled += int(mason_match.group(1))
            if helper_match:
                unskilled += int(helper_match.group(1))

            # Format 2
            skilled_match = re.search(
                r"(?m)^Skilled\s+(\d+)\s*P",
                section,
                re.IGNORECASE

            )
            unskilled_match = re.search(
                r"(?m)^Unskilled\s+(\d+)\s*P",
                section,
                re.IGNORECASE
            )
            if skilled_match:
                skilled += int(skilled_match.group(1))
            if unskilled_match:
                unskilled += int(unskilled_match.group(1))
            print("SKILLED MATCH:", skilled_match.group(1) if skilled_match else None)
            print("UNSKILLED MATCH:", unskilled_match.group(1) if unskilled_match else None)

            # Format 3
            daily_wages_match = re.search(
                r"Daily wages\s+(\d+)\s*P",
                section,
                re.IGNORECASE
            )
            if (
                daily_wages_match
                and skilled == 0
                and unskilled == 0
            ):
                skilled = int(
                    daily_wages_match.group(1)
                )
        print("SECTION TEXT:")
        print(section[:1000])
        print("CONTRACTOR:", contractor)
     
        print("SKILLED:", skilled)
        print("UNSKILLED:", unskilled)
        print("=" * 50)
        daily_records_match = re.search(
            r"Daily Records(.*?)(?:Work Updates|$)",
            section,
            re.DOTALL | re.IGNORECASE
        )
        if daily_records_match:
            daily_text = daily_records_match.group(1)
            blocks = re.split(
                r"(?=Labour\s+(?:Total\s+)?\d+\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))",
                daily_text,
                flags=re.IGNORECASE
            )
        else:
             blocks = []
        contractor_daily_labour[contractor] = {}
        contractor_daily_skilled[contractor] = {}
        contractor_daily_unskilled[contractor] = {}
        for block in blocks:
            attendance_part = block.split("INVENTORY")[0]
            dates = re.findall(
                r"(\d+)\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)",
                attendance_part,
                re.IGNORECASE
            )
            week_dates = [
                (int(day), month.upper())
                for day, month in dates
            ]
            print("CONTRACTOR:", contractor)
            print(attendance_part[:1000])
            if "Daily wages" in attendance_part:
                print("FOUND DAILY WAGES")
            print(attendance_part)
            attendance_rows = []
            for line in attendance_part.splitlines():
                line = re.sub(r"\s+", " ", line.strip())
                if not line:
                    continue
                match_with_p = re.match(
                    r"^([A-Za-z][A-Za-z\s&/-]*?)\s+\d+\s+P\s+((?:\d+\s*)+)$",
                    line,
                    re.IGNORECASE
                )
                if match_with_p:
                    attendance_rows.append(
                        (
                            match_with_p.group(1).strip(),
                            match_with_p.group(2).strip()
                        )
                    )
                    continue
                match_without_p = re.match(
                    r"^([A-Za-z][A-Za-z\s&/-]*?)\s+((?:\d+\s*)+)$",
                    line,
                    re.IGNORECASE
                )
                if match_without_p:
                    values = re.findall(
                        r"\d+",
                        match_without_p.group(2)
                    )
                    if len(values) == len(week_dates):
                        attendance_rows.append(
                            (
                                match_without_p.group(1).strip(),
                                match_without_p.group(2).strip()
                            )
                        )
            print(attendance_part)
            print("CONTRACTOR:", contractor)
            SKILLED_TYPES = [
                "Mason",
                "Skilled",
                "Semi Skilled",
                "Daily Wages",
                "Labour"
            ]
            UNSKILLED_TYPES = [
                "Helper",
                "Unskilled"
            ]
            for row_index, row in enumerate(attendance_rows):
                labour_type = row[0].strip().title()
                values = [
                    int(x)
                    for x in re.findall(r"\d+", row[1])
                ]
                print("CONTRACTOR:", contractor)
                values = values[:len(week_dates)]
                for (day, month), count in zip(week_dates,values):
                    date_key = f"{ordinal(day)} {month.title()} 2026"
                    contractor_daily_labour[contractor][date_key] = (
                        contractor_daily_labour[contractor].get(
                            date_key,
                            0
                        ) + count
                    )
                    if labour_type in SKILLED_TYPES:
                        contractor_daily_skilled[contractor][date_key] = (
                            contractor_daily_skilled[contractor].get(
                                date_key,
                                0
                            ) + count
                        )
                        print(
                        "ADDING SKILLED",
                        contractor,
                        date_key,
                        count
                        )
                    elif labour_type in UNSKILLED_TYPES:
                        contractor_daily_unskilled[contractor][date_key] = (
                            contractor_daily_unskilled[contractor].get(
                                date_key,
                                0
                            ) + count
                        )
                        print(
                            "SKILLED DICT:",
                            contractor,
                            contractor_daily_skilled[contractor]
                        )
        if skilled == 0 and unskilled == 0:
            contractor_labour[contractor] = {
                "skilled": sum(
                    contractor_daily_skilled[contractor].values()
                ),
                "unskilled": sum(
                    contractor_daily_unskilled[contractor].values()
                )
            }
        else:
            contractor_labour[contractor] = {
                "skilled": skilled,
                "unskilled": unskilled
            }          
        print(
        contractor,
        skilled,
        unskilled
        )
        
        
    # Extract daily records

    # pattern = r"(\d{1,2}(?:st|nd|rd|th)\s+May\s+2026).*?Overall Remarks-\s*(.*?)=(\d+\.\d+)\s*sft"

    # print("UPLOAD HIT")

    # matches = re.findall(
    #     pattern,
    #     extracted_text,
    #     re.DOTALL
    # )

    # print("MATCHES FOUND:", len(matches))
    # print(matches)

    records = []

    # for match in matches:

    #     date = match[0]

    #     activity = match[1].strip()

    #     activity = activity.split("\n")[0]

    #     activity = re.sub(
    #         r"\s+\d+.*",
    #         "",
    #         activity
    #     ).strip()

    #     activity = re.sub(
    #         r"-.*",
    #         "",
    #         activity
    #     ).strip()

    #     quantity = float(match[2])
    current_date = ""
    work_updates = extracted_text.split("Work Updates")[-1]

    records = []
    current_contractor = ""
    lines = work_updates.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "Count wise" in line:
            print("RAW",repr(line))
            current_contractor=line
            current_contractor = re.sub(r"\(Count wise\)","", current_contractor).strip()
            print("CONTRACTOR FOUND:", current_contractor)
        date_match = re.search(
        r"\d{1,2}(?:st|nd|rd|th)\s+[A-Za-z]+\s+\d{4}",
        line
        )
        if date_match:
            current_date = date_match.group()
            print(
                "CURRENT:",
                current_contractor,
                "|",
                current_date
            )
        if "Overall Remarks-" in line:
            activity_block = line
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if "Powered by getpowerplay.in" in next_line:
                    break
                if re.search(
                    r"\d{1,2}(?:st|nd|rd|th)\s+[A-Za-z]+\s+\d{4}",
                    next_line
                ):
                    break

                if "Count wise" in next_line:
                    break

                activity_block += " " + next_line
                j += 1
            print(activity_block)
            quantities = re.findall(
                r"=\s*(\d+\.\d+)",
                activity_block
            )
            quantity = sum(
                float(q)
                for q in quantities
            )
            full_remark = activity_block.replace(
                "Overall Remarks-",
                ""
            ).strip()
            print("FULL REMARK:", full_remark)
            print("QUANTITIES FOUND:", quantities)
            activity = activity_block.replace(
                "Overall Remarks-",""
            )
            activity = re.sub(
                r"Powered by getpowerplay\.in.*",
                "",
                activity,
                flags=re.IGNORECASE
            )
            activity = re.sub(
                r"-?\d+.*?=\s*\d+\.\d+\s*(?:sft|rft|cum|sqm)?","",
                activity,
                flags=re.IGNORECASE
            )
            activity = activity.strip(" -")
            print(
                "RECORD:",
                current_contractor,
                contractor_labour.get(current_contractor)
            )
            print(
                "DAILY LABOUR DICT:",
                contractor_daily_labour.get(
                    current_contractor,
                    {}
                )
            )
            print(
                "LABOUR FOR DATE:",
                contractor_daily_labour.get(
                    current_contractor,
                    {}
                ).get(
                    current_date,
                    0
                )
            )
            print("ACTIVITY:", activity)
            print("QUANTITY:", quantity)
            records.append({
                "date": current_date,
                "contractor": current_contractor,
                "quantity": full_remark,
                "quantity_numeric": quantity,
                "skilled": contractor_daily_skilled.get(
                    current_contractor,
                    {}
                ).get(
                    current_date,
                    0
                ),
                "unskilled": contractor_daily_unskilled.get(
                    current_contractor,
                    {}
                ).get(
                    current_date,
                    0
                )
            })
            print("NEW RECORDS BLOCK EXECUTED")
            i = j
            continue
        i += 1
    records.sort(
        key=lambda x: int(
            re.search(r"\d+", x["date"]).group()
            )
            )
    print("FINAL RECORDS:")
    print(records)
    print("RETURNING:")
    print("report_type =", report_type)
    print("monthly_total_labours =", monthly_total_labours)
    print("CONTRACTOR LABOUR:")
    print(contractor_labour)
    print(
        "TOTAL LABOURERS:",
        sum(
            x["skilled"] + x["unskilled"]
            for x in contractor_labour.values()
        )
    )
    print("CONTRACTOR LABOUR FINAL:")
    print(contractor_labour)
    contractor_summary = []
    for contractor, labour in contractor_labour.items():
        skilled = labour.get("skilled", 0)
        unskilled = labour.get("unskilled", 0)
        contractor_summary.append({
        "contractor": contractor,
        "skilled": skilled,
        "unskilled": unskilled,
        "total": skilled + unskilled
        })
    print(
    "SKILLED LABOUR:",
    sum(x["skilled"] for x in contractor_labour.values())
    )
    print(
    "UNSKILLED LABOUR:",
    sum(x["unskilled"] for x in contractor_labour.values())
    )
    print(
    "TOTAL LABOURERS:",
    sum(
        x["skilled"] + x["unskilled"]
        for x in contractor_labour.values()
        )
    )
    print("CONTRACTOR SUMMARY:", contractor_summary)
    return {
    "report_type": report_type,
    "site": site,
    "contractor": contractors,
    "type_of_work": "Contract",

    "skilled_labour": sum(
        x["skilled"]
        for x in contractor_labour.values()
    ),

    "unskilled_labour": sum(
        x["unskilled"]
        for x in contractor_labour.values()
    ),

    "total_labourers": sum(
        x["skilled"] + x["unskilled"]
        for x in contractor_labour.values()
    ),

    "contractor_summary": contractor_summary,

    "records": records
}