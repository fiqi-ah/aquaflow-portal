from models import Invoice

def generate_iif_string(invoices: list[Invoice]) -> str:
    """
    Converts approved invoices to QuickBooks IIF format.
    Assumes a fixed rate per bottle (default $1.00). 
    Adjust RATE_PER_BOTTLE below to match your pricing.
    """
    if not invoices:
        return ""

    RATE_PER_BOTTLE = 1.00  # CHANGE THIS TO YOUR ACTUAL PRICE
    
    header = "!TRNS\tTRANS DATE\tREF NUM\tNAME\tAMOUNT\tTAX AMOUNT\n"
    lines = []

    for inv in invoices:
        date_str = inv.created_at.strftime("%m/%d/%Y")
        
        # Calculate total amount based on quantity
        total_amount = inv.bottles_delivered * RATE_PER_BOTTLE
        
        # Ref Num helps trace back to the specific delivery record
        ref_num = f"{inv.customer_id}-DEL-{inv.id}"
        
        row = f"INVOICE\t{date_str}\t{ref_num}\t{inv.customer_name}\t{total_amount:.2f}\t0.00"
        lines.append(row)
        
    body = "\n".join(lines)
    footer = "\n!ENDTRNS"
    
    return header + body + footer