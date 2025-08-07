from datetime import date

def get_tax_year_dates(year=None):
    if year is None:
        today = date.today()
        if today.month < 4 or (today.month == 4 and today.day < 6):
            year = today.year - 1
        else:
            year = today.year
    
    start_date = date(year, 4, 6)
    end_date = date(year + 1, 4, 5)
    
    return (start_date, end_date)