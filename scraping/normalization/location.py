from scraping.normalization.cleaners import clean_text

US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA",
    "ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK",
    "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
}

def parse_city_state(text: str):
    """
    Input examples:
      "Dallas, TX" -> ("Dallas", "TX")
      "Austin, Texas" -> ("Austin", "")
    We only lock 2-letter states here; richer mapping comes later.
    """
    text = clean_text(text)
    if "," not in text:
        return ("", "")
    city, state = [clean_text(x) for x in text.split(",", 1)]
    state = state.upper()
    if state in US_STATES:
        return (city, state)
    return (city, "")
