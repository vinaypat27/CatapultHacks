DOMAIN_CATEGORIES = {
    "general": [],
    "healthcare": {
        "high": [r"\bHIPAA\b", r"\bAudit Rights\b", r"\bIndemnification\b"],
        "medium": [r"\bInsurance\b", r"\bCompliance\b", r"\bProtected Health Information\b"]
    },
    "education": {
        "high": [r"\bFERPA\b", r"\bEffective Date\b", r"\bExpiration Date\b"],
        "medium": [r"\bAudit Rights\b", r"\bAcademic\b", r"\bStudent Data\b"]
    },
    "banking": {
        "high": [r"\bGDPR\b", r"\bAudit Rights\b", r"\bTermination For Convenience\b"],
        "medium": [r"\bInsurance\b", r"\bFinancial Data\b", r"\bAML\b", r"\bKYC\b"]
    },
    "law": {
        "high": [r"\bGoverning Law\b", r"\bIndemnification\b", r"\bTermination For Convenience\b"],
        "medium": [r"\bArbitration\b", r"\bJurisdiction\b", r"\bLegal Counsel\b"]
    },
    "nda": {
        "high": [r"\bNon-Compete\b", r"\bNon-Disparagement\b", r"\bNo-Solicit Of Employees\b", r"\bNo-Solicit Of Customers\b"],
        "medium": [r"\bConfidential Information\b", r"\bProprietary Information\b", r"\bMutual NDA\b"]
    },
    "marketing": {
        "high": [r"\bbrand\b", r"\bpromotion\b", r"\bendorsement\b", r"\bmarketing\b", r"\badvertising\b", r"\bsponsorship\b"],
        "medium": [r"\bcampaign\b", r"\bvisibility\b", r"\bPR\b"]
    },
    "partnership": {
        "high": [r"\baffiliate\b", r"\bfranchise\b", r"\bjoint venture\b", r"\balliance\b", r"\breseller\b"],
        "medium": [r"\bpartner\b", r"\bpartnership\b", r"\bcollaboration\b"]
    },
    "technology": {
        "high": [r"\bIP\b", r"\boutsourcing\b", r"\bmaintenance\b", r"\bhosting\b", r"\bSLA\b"],
        "medium": [r"\btech support\b", r"\bsystem uptime\b", r"\bdata center\b"]
    },
    "supply_chain": {
        "high": [r"\bmanufacturing\b", r"\bsupply\b", r"\btransportation\b", r"\blogistics\b"],
        "medium": [r"\binventory\b", r"\bproduction\b", r"\bdelivery\b"]
    },
    "legal": {
        "high": [r"\blicense\b", r"\bnon-compete\b", r"\bnon-solicit\b", r"\bIP rights\b"],
        "medium": [r"\bconfidentiality\b", r"\buse rights\b", r"\btermination\b"]
    },
    "distribution": {
        "high": [r"\bdistributor\b", r"\bdistribution\b", r"\bchannels\b"],
        "medium": [r"\bdeployment\b", r"\bmarket reach\b", r"\bdevelopment\b"]
    }
}

DOMAIN_KEYWORDS = {
    "healthcare": [r"\bHIPAA\b", r"\bheath\b", r"\bpatient\b", r"\bmedical\b"],
    "education": [r"\bschool\b", r"\bstudent\b", r"\beducation\b", r"\bFERPA\b"],
    "banking": [r"\bbank\b", r"\bfinancial\b", r"\bcredit\b", r"\bdebit\b", r"\bGDPR\b"],
    "law": [r"\blaw firm\b", r"\blegal\b", r"\bgoverning law\b", r"\bjurisdiction\b"],
    "nda": [r"\bconfidentiality\b", r"\bnon-disclosure\b", r"\bnon-compete\b", r"\bno-solicit\b"]
}
