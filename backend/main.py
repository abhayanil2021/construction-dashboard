from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
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

    # Site
    lines = [
    line.strip()
    for line in extracted_text.split("\n")
    if line.strip()
    ]
    site = "Unknown Site"
    for i, line in enumerate(lines):
        if "DAILY PROGRESS REPORT" in line.upper():
            if i + 1 < len(lines):
                site = lines[i + 1]
            break
    print("SITE FOUND:", site)

    # Contractor
    contractors = re.findall(
    r"([A-Za-z ]+?)\s+(?:SC|1)?\(Count wise\)",
    extracted_text
    )
    print("CONTRACTORS:")
    print(contractors)
    contractor_labour = {}

    # Skilled Labour
    for idx, contractor in enumerate(contractors):
        start = extracted_text.find(contractor)
        if idx < len(contractors) - 1:
            end = extracted_text.find(
                contractors[idx + 1]
            )
            section = extracted_text[start:end]
        else:
            section = extracted_text[start:]

        skilled = 0
        unskilled = 0
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
        contractor_labour[contractor] = {
            "skilled": skilled,
            "unskilled": unskilled
        }
    print(contractor_labour)

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

    #     records.append({
    #         "date": date,
    #         "activity": activity,
    #         "quantity": quantity
    #     })
    current_date = ""
    work_updates = extracted_text.split("Work Updates")[-1]

    records = []
    current_contractor = ""
    lines = work_updates.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        print("LINE:", line)
        if "Count wise" in line:
            current_contractor = re.sub(
                r"\s+(SC|1)\(Count wise\)",
                "",
                line
                ).strip()
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
            print("FULL BLOCK:")
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
            records.append({
                "date": current_date,
                "contractor": current_contractor,
                "activity": activity,
                "quantity": float(quantity),
                "remark": full_remark,
                "skilled": contractor_labour.get(
                    current_contractor,
                    {}
                ).get("skilled", 0),
                "unskilled": contractor_labour.get(
                    current_contractor,
                    {}
                ).get("unskilled", 0)
            })
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
    return {
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
        "records": records
    }