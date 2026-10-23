from fastapi import FastAPI

app = FastAPI(
    title="BloodLink",
    description=(
        "Academic Blood Bank Management System for STQA. Educational demonstration only: "
        "not a clinical transfusion decision system."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
