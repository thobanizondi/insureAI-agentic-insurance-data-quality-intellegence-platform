
import pandas as pd

from src.utils.security_audit import audit_event


SENSITIVE_COLUMNS = {
    "customer_name",
    "credit_score",
    "national_id",
    "id_number",
    "identity_number",
    "sa_id_number",
    "email",
    "email_address",
    "phone",
    "phone_number",
    "mobile_number",
    "address",
    "physical_address",
    "bank_account",
    "account_number",
}


def mask_customer_name(value):
    if pd.isna(value):
        return value

    words = str(value).split()

    return " ".join(
        word[0] + "*" * max(len(word) - 1, 3)
        for word in words
    )


def mask_sensitive_data(dataframe):
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Data masking requires a pandas DataFrame.")

    masked_dataframe = dataframe.copy(deep=True)
    masked_columns = []

    for column in masked_dataframe.columns:
        normalized_column = str(column).strip().lower()

        if normalized_column not in SENSITIVE_COLUMNS:
            continue

        if normalized_column == "customer_name":
            masked_dataframe[column] = (
                masked_dataframe[column].apply(mask_customer_name)
            )
        else:
            masked_dataframe[column] = masked_dataframe[column].apply(
                lambda value: "********" if pd.notna(value) else value
            )

        masked_columns.append(str(column))

    if masked_columns:
        audit_event(
            event="data_masking",
            status="success",
            details=(
                f"Masked {len(masked_columns)} sensitive columns: "
                + ", ".join(masked_columns)
            )
        )

    return masked_dataframe
