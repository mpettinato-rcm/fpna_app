from .db import fetch_companies

def company_context(request):
    """
    Context processor to add company data to all templates
    """
    try:
        companies = fetch_companies()
        
        # Get selected company from session, default to AFP
        selected_company = request.session.get('selected_company', 'AFP')
        
        # Ensure selected company exists in the list
        if selected_company not in companies:
            selected_company = companies[0] if companies else 'AFP'
            request.session['selected_company'] = selected_company
        
        return {
            'companies': companies,
            'selected_company': selected_company,
        }
    except Exception as e:
        # Fallback in case of database issues
        return {
            'companies': ['AFP'],
            'selected_company': 'AFP',
        }