"""
Seed script to populate Scheme table with government subsidies and schemes data.
Run this after migrations: python seed_schemes.py
"""
import json
from extensions import db
from models import Scheme
from app import app

def seed_schemes():
    """Add sample schemes and subsidies to the database"""
    
    schemes_data = [
        {
            'scheme_code': 'pmkisan',
            'name': 'PM-KISAN Samman Nidhi',
            'description': 'A central sector scheme providing direct income support of ₹6,000 per year to all landholding farmer families across the country. This amount is transferred in three equal installments of ₹2,000 each to eligible farmers directly in their bank accounts.',
            'scheme_type': 'subsidy',
            'focus_area': 'Income Support',
            'focus_color': '#fbc02d',
            'benefit_amount': '₹6,000/year (₹2,000 x 3 installments)',
            'eligibility_criteria': 'All landholding farmer families with land records in their name, having cultivable land in the country',
            'apply_steps': [
                'Visit https://pmkisan.gov.in or your nearest CSC center',
                'Click on "New Farmer Registration"',
                'Enter Aadhaar number and mobile number',
                'Fill in personal, bank and land details',
                'Submit and receive acknowledgment'
            ],
            'external_link': 'https://pmkisan.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Aadhaar Card', 'Land documents/LPC', 'Bank Account (IFSC Code)', 'Mobile number']
        },
        {
            'scheme_code': 'nmeo',
            'name': 'National Mission on Edible Oils - Oil Palm (NMEO-OP)',
            'description': 'Scheme to promote cultivation of oilseeds including oil palm through area expansion and productivity enhancement. Provides subsidized seeds, financial incentives, and technical support to farmers switching to oilseed production.',
            'scheme_type': 'scheme',
            'focus_area': 'Crop Switch',
            'focus_color': '#4caf50',
            'benefit_amount': '₹4,500-7,500 incentive + Free Seeds',
            'eligibility_criteria': 'Farmers in oilseed promotion states (Including Maharashtra, Odisha, AP, TG, MP)',
            'apply_steps': [
                'Contact District Agriculture Office or Krishi Vigyan Kendra',
                'Submit filled application form with land documents',
                'Attend mandatory training on oilseed cultivation',
                'Field verification and approval of application',
                'Receive seeds and financial assistance'
            ],
            'external_link': 'https://agricoop.nic.in/programmes-schemes-listing/national-mission-on-oilseeds-and-oil-palm-nmoop',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Land record/7-12 extract', 'Aadhar Card', 'Bank passbook', 'Training certificate']
        },
        {
            'scheme_code': 'smam',
            'name': 'Sub-Mission on Agricultural Mechanization (SMAM)',
            'description': 'Aims to increase farm mechanization by providing subsidy (40-80% depending on category) for agricultural machinery and equipment. Helps farmers reduce cost of production and improve efficiency.',
            'scheme_type': 'subsidy',
            'focus_area': 'Equipment',
            'focus_color': '#e64a19',
            'benefit_amount': '40-80% Subsidy on Machinery',
            'eligibility_criteria': 'Individual farmers, SCs/STs, Marginal & Small farmers, and FPOs in SMAM registered zones',
            'apply_steps': [
                'Check eligibility and available machinery on state SMAM portal',
                'Register on the state Department of Agriculture website',
                'Submit application with land proof and identify proof',
                'Select machinery and authorized vendor',
                'Make payment after receiving sanction and purchase'
            ],
            'external_link': 'https://smam.gov.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Land ownership proof/LPC', 'Aadhar Card', 'Bank account details', 'Identity proof']
        },
        {
            'scheme_code': 'pmfby',
            'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
            'description': 'Comprehensive crop insurance scheme providing protection against yield losses due to natural calamities, pests and diseases. Covers both loanee and non-loanee farmers growing notified crops.',
            'scheme_type': 'scheme',
            'focus_area': 'Insurance',
            'focus_color': '#795548',
            'benefit_amount': 'Comprehensive crop insurance coverage',
            'eligibility_criteria': 'All farmers growing notified crops in the area, both loanee and non-loanee',
            'apply_steps': [
                'For loanee farmers: Automatic coverage through bank',
                'For non-loanee: Visit nearest bank or CSC with crop details',
                'Fill form with crop, area and insurance premium details',
                'Submit documents and receive policy within 15 days',
                'Premium payment can be done online or offline'
            ],
            'external_link': 'https://pmfby.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Crop details', 'Land area/Area certificate', 'ID proof', 'Bank details']
        },
        {
            'scheme_code': 'perdrop',
            'name': 'Per Drop More Crop (PMKSY-AIBP)',
            'description': 'Micro-irrigation scheme promoting drip and sprinkler systems to save water and increase productivity. Provides 50-80% subsidy on micro-irrigation systems installation depending on farmer category.',
            'scheme_type': 'subsidy',
            'focus_area': 'Irrigation',
            'focus_color': '#2196f3',
            'benefit_amount': '50-80% subsidy on system cost',
            'eligibility_criteria': 'Farmers with assured water source and command area suitable for micro-irrigation',
            'apply_steps': [
                'Apply through state irrigation department portal or online',
                'Submit water source proof and field survey report',
                'Get field verification done by department officer',
                'Select approved vendor and place order',
                'Get subsidy released after installation verification'
            ],
            'external_link': 'https://aibp.nic.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Water source proof', 'Land proof', 'Survey report', 'Vendor quotation']
        },
        {
            'scheme_code': 'soilhealth',
            'name': 'Soil Health Card Scheme',
            'description': 'Provides free soil testing to farmers to assess soil nutrient status and fertility. Farmers receive personalized recommendations for crop-specific fertilizer and nutrient management through Soil Health Cards.',
            'scheme_type': 'scheme',
            'focus_area': 'Soil Management',
            'focus_color': '#8bc34a',
            'benefit_amount': 'Free soil testing & advisory for 2 years',
            'eligibility_criteria': 'All farmers without any financial limit',
            'apply_steps': [
                'Contact District Soil Testing Lab or Local KVK',
                'Register and schedule soil sample collection',
                'Soil samples collected and tested at certified lab',
                'Receive Soil Health Card with fertilizer recommendations',
                'Follow recommendations for optimal productivity'
            ],
            'external_link': 'https://soilhealth.dac.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Land proof', 'Aadhar Card', 'Mobile number']
        },
        {
            'scheme_code': 'aif',
            'name': 'Agri Infrastructure Fund (AIF)',
            'description': 'Provides concessional financing at 3% interest subvention for creation of farm-gate and aggregation infrastructure. Covers post-harvest equipment, cold storage, processing units, and community farming assets.',
            'scheme_type': 'subsidy',
            'focus_area': 'Infrastructure',
            'focus_color': '#607d8b',
            'benefit_amount': '3% interest subvention + collateral-free loan up to ₹2 crore',
            'eligibility_criteria': 'Individual entrepreneurs, startups, FPOs, PACS, Primary agricultural cooperatives',
            'apply_steps': [
                'Prepare detailed project report (DPR) with cost estimates',
                'Approach any scheduled bank for loan',
                'Submit bank loan letter on AIF portal with DPR',
                'Register project on aif.nic.in',
                'Interest subvention credited after loan disbursement'
            ],
            'external_link': 'https://agriinfra.dac.gov.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Project DPR', 'Bank loan sanction letter', 'Land proof', 'Company registration']
        },
        {
            'scheme_code': 'beekeeping',
            'name': 'Pradhan Mantri Kisan Samridhi Yojana (Beekeeping)',
            'description': 'Promotes scientific beekeeping for honey and pollination services. Provides subsidy for bee colonies, boxes, equipment, and processing units. Generates additional income for farmers as allied activity.',
            'scheme_type': 'subsidy',
            'focus_area': 'Allied Agriculture',
            'focus_color': '#ffc107',
            'benefit_amount': '₹3,000-4,000 subsidy per bee colony + Equipment subsidy',
            'eligibility_criteria': 'Farmers interested in beekeeping in suitable zones with vegetable/fruit growing',
            'apply_steps': [
                'Contact state Horticulture or Agriculture Department',
                'Complete beekeeping training program (mandatory)',
                'Submit application with training certificate',
                'Plan bee apiary placement on your farm',
                'Receive subsidized bee colonies and equipment'
            ],
            'external_link': 'https://www.dahd.nic.in/beekeeping',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Training completion certificate', 'Land proof', 'Aadhar Card', 'Bank details']
        },
        {
            'scheme_code': 'kcc',
            'name': 'Kisan Credit Card (KCC) Scheme',
            'description': 'Provides adequate and timely credit for all agricultural activities. Covers crop production needs, farm maintenance, working capital, and minor farm infrastructure investments at subsidized rates.',
            'scheme_type': 'subsidy',
            'focus_area': 'Credit Access',
            'focus_color': '#3f51b5',
            'benefit_amount': 'Flexible credit limit at 7% interest rate',
            'eligibility_criteria': 'Individual farmers, tenant farmers, and groups with operational holdings',
            'apply_steps': [
                'Visit nearest bank branch',
                'Fill KCC application form with farm details',
                'Submit land proof and identity documents',
                'Bank conducts verification and assessment',
                'Receive KCC with credit limit within 7 days'
            ],
            'external_link': 'https://www.rbi.org.in/en/web/base/notification/prs_pressrelease_25032020',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Land record/LPC', 'Aadhar Card', 'ID proof', 'Last 3 bank statements']
        },
        {
            'scheme_code': 'rpds',
            'name': 'Rashtriya Pashudhan Vikas Scheme',
            'description': 'Aimed at boosting livestock productivity and yield through subsidies on quality breeding materials. Provides financial assistance for livestock development as allied sector income.',
            'scheme_type': 'subsidy',
            'focus_area': 'Livestock',
            'focus_color': '#e91e63',
            'benefit_amount': '₹15,000-50,000 subsidy for quality animals',
            'eligibility_criteria': 'Farmers with agriculture holdings interested in livestock integration',
            'apply_steps': [
                'Contact District Animal Husbandry Office',
                'Attend training on livestock management',
                'Submit application with farm details',
                'Participate in animal selection from approved breeders',
                'Receive animal with subsidy on purchase'
            ],
            'external_link': 'https://www.dahd.nic.in/livestock-schemes',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Land proof', 'Training certificate', 'Aadhar Card', 'Bank account details']
        },
        {
            'scheme_code': 'pmmsy',
            'name': 'Pradhan Mantri Matsya Sampada Yojana (PMMSY)',
            'description': 'Comprehensive scheme for sustainable development of marine and inland fisheries. Promotes fish farming and provides subsidies for cold storage, fish processing units, and fishing equipment.',
            'scheme_type': 'scheme',
            'focus_area': 'Fisheries',
            'focus_color': '#00bcd4',
            'benefit_amount': '₹3 lakh - ₹10 lakh subsidy for infrastructure',
            'eligibility_criteria': 'Fish farmers, fish traders, SHG members, FPOs in coastal and inland areas',
            'apply_steps': [
                'Contact State Fisheries Department or Krishi Vigyan Kendra',
                'Prepare project proposal with cost estimates',
                'Submit application with necessary documents',
                'Get field inspection and approval',
                'Receive subsidy disbursement for approved projects'
            ],
            'external_link': 'https://www.pmmsy.dof.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Project proposal', 'Land proof', 'Aadhar Card', 'Bank account details']
        },
        {
            'scheme_code': 'pkvy',
            'name': 'Paramparagat Krishi Vikas Yojana (PKVY)',
            'description': 'Scheme to promote organic farming through cluster-based approach. Provides subsidy for organic farming practices including purchase of organic inputs and certification.',
            'scheme_type': 'subsidy',
            'focus_area': 'Organic Farming',
            'focus_color': '#8bc34a',
            'benefit_amount': '₹50,000/hectare subsidy for 3 years',
            'eligibility_criteria': 'Farmers in group of minimum 10-50 farmers interested in organic farming',
            'apply_steps': [
                'Form or join farmer group of minimum 10 farmers',
                'Contact District Agriculture Officer',
                'Submit cluster proposal with land documents',
                'Attend organic farming training',
                'Receive subsidy for certified organic farming'
            ],
            'external_link': 'https://www.dac.gov.in/en/schemes/paramparagat-krishi-vikas-yojana',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Group formation certificate', 'Land proof of all members', 'Training certificate']
        },
        {
            'scheme_code': 'pmmb',
            'name': 'Pradhan Mantri Adarsh Gram Yojana',
            'description': 'Community development scheme aimed at creating model villages with improved agricultural practices, infrastructure, and livelihood opportunities for farmers.',
            'scheme_type': 'scheme',
            'focus_area': 'Rural Development',
            'focus_color': '#4caf50',
            'benefit_amount': 'Infrastructure development support + Training',
            'eligibility_criteria': 'Villages with minimum 500-1000 families, willing for community participation',
            'apply_steps': [
                'Gram Panchayat applies to District Administration',
                'Submit village development plan and budget',
                'Get approval from State Government',
                'Implement agricultural and infrastructure projects',
                'Monitor and evaluate progress'
            ],
            'external_link': 'https://www.india.gov.in/official-website-pradhan-mantri-adarsh-gram-yojana',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Gram Panchayat resolution', 'Village census data', 'Development plan']
        },
        {
            'scheme_code': 'ondc',
            'name': 'Open Network for Digital Commerce (ONDC)',
            'description': 'Digital commerce network enabling small farmers and merchants to sell directly to consumers without platform dependency. Facilitates direct farmer-to-consumer transactions reducing middlemen.',
            'scheme_type': 'scheme',
            'focus_area': 'Digital Commerce',
            'focus_color': '#673ab7',
            'benefit_amount': 'Zero commission platform + Direct market access',
            'eligibility_criteria': 'Registered farmers, agricultural producers, merchants with GST/Aadhar',
            'apply_steps': [
                'Register on ONDC platform (ondc.org)',
                'Create seller profile with business details',
                'Add agricultural products with descriptions and prices',
                'Get verified by platform through GST/business documents',
                'Start selling directly to consumers'
            ],
            'external_link': 'https://www.ondc.org/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['GST Certificate or Aadhar', 'Bank account details', 'Product details']
        },
        {
            'scheme_code': 'pmfaad',
            'name': 'PM Formalization of Micro Food Enterprises (PMFME)',
            'description': 'Scheme to support micro food enterprises including farm-based processing units. Provides subsidy, credit linkage, and training for food processing and value addition.',
            'scheme_type': 'subsidy',
            'focus_area': 'Food Processing',
            'focus_color': '#ff9800',
            'benefit_amount': '₹40,000-₹1 lakh subsidy + Credit linkage',
            'eligibility_criteria': 'Individual farmers, SHGs doing food processing, registered enterprises in FSSAI approved units',
            'apply_steps': [
                'Get FSSAI food business registration',
                'Apply through MSME portal or District Industries Center',
                'Submit business plan and cost estimates',
                'Get inspection and approval of unit',
                'Receive subsidy and bank credit linkage'
            ],
            'external_link': 'https://pmfme.mca.gov.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['FSSAI registration', 'Business plan', 'Aadhar Card', 'Land proof']
        },
        {
            'scheme_code': 'e2e',
            'name': 'e-NAM (Electronic National Agricultural Market)',
            'description': 'Unified online market platform for agricultural commodities. Enables farmers to sell directly to buyers across state borders, reducing middlemen and getting fair prices.',
            'scheme_type': 'scheme',
            'focus_area': 'Market Access',
            'focus_color': '#2196f3',
            'benefit_amount': 'Direct market access + 1-2% commission only',
            'eligibility_criteria': 'Registered farmers with Aadhar and bank account, agricultural traders, exporters',
            'apply_steps': [
                'Register on e-NAM portal (enam.gov.in)',
                'Complete KYC with Aadhar and bank details',
                'List agricultural commodities with quality grades',
                'Create bidding account with registered buyers',
                'Receive bids and complete transactions online'
            ],
            'external_link': 'https://enam.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Aadhar Card', 'Bank account details', 'Farmer registration']
        },
        {
            'scheme_code': 'poshan',
            'name': 'Rashtriya Poshan Abhiyaan (POSHAN)',
            'description': 'Nutrition scheme promoting nutrient-rich crop cultivation and farmer income. Encourages cultivation of pulses, vegetables, fruits improving farm productivity and nutrition.',
            'scheme_type': 'scheme',
            'focus_area': 'Nutrition & Agriculture',
            'focus_color': '#f44336',
            'benefit_amount': 'Training + Seeds subsidy + Market support',
            'eligibility_criteria': 'Farmers willing to cultivate nutrient-rich crops including pulses, vegetables, millets',
            'apply_steps': [
                'Contact District Agriculture Department',
                'Attend nutrition and farming training workshop',
                'Register for nutrient crop cultivation program',
                'Receive subsidized seeds and technical support',
                'Get market linkage support for products'
            ],
            'external_link': 'https://www.dac.gov.in/en/schemes/rashtriya-poshan-abhiyaan-poshan',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Training attendance certificate', 'Land proof', 'Aadhar Card']
        },
        {
            'scheme_code': 'mgnrega',
            'name': 'Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)',
            'description': 'Employment guarantee scheme providing 100 days employment in farm/non-farm work annually. Farmers can work for wages including farm preparation and maintenance work.',
            'scheme_type': 'subsidy',
            'focus_area': 'Rural Employment',
            'focus_color': '#607d8b',
            'benefit_amount': '₹205-258/day for 100 days employment',
            'eligibility_criteria': 'Landless agricultural laborers, marginal farmers, rural household members (18+)',
            'apply_steps': [
                'Register at Gram Panchayat MGNREGA office',
                'Get MGNREGA job card issued (free)',
                'Request work through Gram Panchayat',
                'Work allocated within 15 days of application',
                'Wage payment directly to bank account'
            ],
            'external_link': 'https://www.nrega.nic.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Aadhar Card', 'Voter ID or other ID proof', 'Bank account details']
        },
        {
            'scheme_code': 'atma',
            'name': 'Agricultural Technology Management Agency (ATMA)',
            'description': 'Technology dissemination scheme providing free training and advisory for improved farming practices. Promotes adoption of new crop varieties, techniques, and pest management.',
            'scheme_type': 'scheme',
            'focus_area': 'Technology & Training',
            'focus_color': '#9c27b0',
            'benefit_amount': 'Free training + Advisory + Demo plots',
            'eligibility_criteria': 'All farmers without restriction seeking agricultural technology adoption',
            'apply_steps': [
                'Contact local ATMA center or Block Agriculture Office',
                'Enroll in training program for your crop/area',
                'Attend workshops on improved farming techniques',
                'Participate in demonstration plots',
                'Get ongoing advisory support from block technicians'
            ],
            'external_link': 'https://www.dac.gov.in/en/schemes/agricultural-technology-management-agency-atma',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Aadhar Card', 'Land proof (optional for training)']
        },
        {
            'scheme_code': 'pradhanmantri_krishi_sinchayee_yojana',
            'name': 'Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)',
            'description': 'Irrigation infrastructure development scheme ensuring "Per Drop More Crop". Provides subsidy for water harvesting, borewell, and irrigation system development.',
            'scheme_type': 'subsidy',
            'focus_area': 'Irrigation Infrastructure',
            'focus_color': '#00bcd4',
            'benefit_amount': '50-90% subsidy on water source development',
            'eligibility_criteria': 'Farmers with drought-prone or rainfed agriculture areas, willing to invest in irrigation',
            'apply_steps': [
                'Apply through State Water Resource or Agriculture Department',
                'Submit water source survey and project cost details',
                'Get field inspection by technical team',
                'Approval and subsidy sanction after verification',
                'Construct water harvesting or irrigation system'
            ],
            'external_link': 'https://pmksy.gov.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Water survey report', 'Land proof', 'Aadhar Card', 'Cost estimate']
        },
        {
            'scheme_code': 'kisan_vikas_patra',
            'name': 'Kisan Vikas Patra (KVP)',
            'description': 'Government savings scheme for farmers providing fixed returns and tax benefits. Funds can be used for agricultural purposes with guaranteed doubling in 10-11 years.',
            'scheme_type': 'subsidy',
            'focus_area': 'Financial Security',
            'focus_color': '#ff6f00',
            'benefit_amount': '7.4% interest rate with guaranteed doubling',
            'eligibility_criteria': 'Farmers and agricultural workers aged 18+ with individual savings capacity',
            'apply_steps': [
                'Visit any post office or authorized bank',
                'Fill KVP application form with farmer/AGR details',
                'Deposit minimum ₹1000 (max no limit)',
                'Receive KVP certificate with maturity date',
                'Get guaranteed return after maturity period'
            ],
            'external_link': 'https://www.indiapost.gov.in/financial-services/pages/content/kisan-vikas-patra',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Aadhar Card', 'Bank account details', 'PAN (optional)']
        },
        {
            'scheme_code': 'sabla',
            'name': 'Scheme for Agricultural Bioprospecting and Large-scale Agro-biodiversity (SABL)',
            'description': 'Scheme promoting conservation and sustainable use of agricultural biodiversity. Provides support for farmers maintaining traditional crop varieties and agricultural biodiversity.',
            'scheme_type': 'scheme',
            'focus_area': 'Biodiversity Conservation',
            'focus_color': '#4caf50',
            'benefit_amount': '₹5000-10000 annual support for biodiversity maintenance',
            'eligibility_criteria': 'Farmers practicing traditional agriculture, maintaining heirloom varieties, seed savers',
            'apply_steps': [
                'Contact District Agriculture Office or Community Seed Bank',
                'Document traditional varieties maintained',
                'Submit application with crop details and photographs',
                'Get verification from agricultural expert',
                'Receive support and recognition for conservation'
            ],
            'external_link': 'https://www.dac.gov.in/en/schemes/sabl',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Biodiversity documentation', 'Aadhar Card', 'Land proof']
        },
        {
            'scheme_code': 'national_agricultural_market',
            'name': 'National Agricultural Market (NAM)',
            'description': 'Agricultural marketing scheme creating network of physical markets. Improves market access, price discovery, and reduces post-harvest losses for farmers.',
            'scheme_type': 'scheme',
            'focus_area': 'Market Development',
            'focus_color': '#558b2f',
            'benefit_amount': 'Market infrastructure + Direct buyer access',
            'eligibility_criteria': 'Farmers with agricultural produce, traders, agricultural exporters',
            'apply_steps': [
                'Locate nearest NAM market yard in your district',
                'Get seller registration at market committee',
                'Submit agricultural produce for quality grading',
                'Participate in open bidding by registered buyers',
                'Get fair market price payment through market'
            ],
            'external_link': 'https://nam.indiamart.com/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Farmer ID/Agricultural registration', 'Aadhar Card', 'Bank account']
        },
        {
            'scheme_code': 'dairy_scheme',
            'name': 'National Dairy Plan (NDP)',
            'description': 'Comprehensive scheme supporting dairy farming through productivity enhancement and market linkage. Provides subsidy for dairy cattle, fodder, milk collection units.',
            'scheme_type': 'subsidy',
            'focus_area': 'Dairy Farming',
            'focus_color': '#ffd54f',
            'benefit_amount': '₹60,000-₹90,000 subsidy per dairy animal',
            'eligibility_criteria': 'Farmers interested in dairy farming with suitable land and labor availability',
            'apply_steps': [
                'Contact District Animal Husbandry or Dairy Development Officer',
                'Attend dairy farming training workshop',
                'Prepare dairy unit plan with infrastructure details',
                'Get field inspection and approval',
                'Receive subsidized animals and equipment'
            ],
            'external_link': 'https://www.dahd.nic.in/dairy-scheme',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Training certificate', 'Land proof', 'Aadhar Card', 'Bank account']
        },
        {
            'scheme_code': 'horticulture',
            'name': 'Mission for Integrated Development of Horticulture (MIDH)',
            'description': 'Comprehensive horticulture development scheme covering fruits, vegetables, flowers, spices, and plantation crops. Provides subsidy for crop establishment and infrastructure.',
            'scheme_type': 'subsidy',
            'focus_area': 'Horticulture',
            'focus_color': '#e91e63',
            'benefit_amount': '₹1-3 lakh subsidy per hectare for horticulture crops',
            'eligibility_criteria': 'Farmers willing to cultivate fruits, vegetables, flowers, spices, plantation crops',
            'apply_steps': [
                'Contact District Horticulture Department',
                'Select horticulture crop suitable for your area',
                'Submit land and crop details with nursery quote',
                'Get field verification and approval',
                'Receive plants and financial support for establishment'
            ],
            'external_link': 'https://www.midh.gov.in/',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Land proof', 'Aadhar Card', 'Crop selection certificate', 'Nursery quotation']
        },
        {
            'scheme_code': 'rashtriya_krishi_vikas_yojana',
            'name': 'Rashtriya Krishi Vikas Yojana (RKVY)',
            'description': 'Agricultural development scheme providing flexibility in resource allocation for state-specific agricultural programs. Focuses on productivity enhancement and agricultural innovation.',
            'scheme_type': 'scheme',
            'focus_area': 'Agricultural Innovation',
            'focus_color': '#1976d2',
            'benefit_amount': 'Infrastructure + Technology + Market linkage support',
            'eligibility_criteria': 'State governments, agricultural organizations, farmer groups for approved projects',
            'apply_steps': [
                'State/District submits agricultural development projects',
                'Project evaluation by RKVY planning committee',
                'Approval and fund allocation for selected projects',
                'Implementation at state/district level',
                'Beneficiary farmers receive support through programs'
            ],
            'external_link': 'https://rkvy.nic.in/',
            'is_recommended': False,
            'is_active': True,
            'required_documents': ['Project proposal', 'Cost-benefit analysis', 'Implementation plan']
        },
        {
            'scheme_code': 'natural_farming',
            'name': 'Scheme for Promotion of Natural Farming',
            'description': 'Promotes sustainable natural farming practices without chemical fertilizers and pesticides. Provides training and subsidy for natural farming inputs like vermicompost, bio-manure.',
            'scheme_type': 'subsidy',
            'focus_area': 'Natural Farming',
            'focus_color': '#6d4c41',
            'benefit_amount': '₹50,000/hectare for 3 years support',
            'eligibility_criteria': 'Farmers willing to adopt natural farming methods with minimum 0.5 hectare land',
            'apply_steps': [
                'Contact District Agriculture Department',
                'Attend natural farming training and awareness workshop',
                'Register for the natural farming promotion scheme',
                'Get baseline soil and crop health documentation',
                'Receive natural farming inputs and technical support'
            ],
            'external_link': 'https://www.dac.gov.in/en/schemes/scheme-promotion-natural-farming-across-india',
            'is_recommended': True,
            'is_active': True,
            'required_documents': ['Training attendance', 'Land proof', 'Aadhar Card', 'Soil health report']
        }
    ]

    with app.app_context():
        # Check if schemes already exist
        existing_count = Scheme.query.count()
        if existing_count > 0:
            print(f'Schemes already exist ({existing_count} records). Skipping seed...')
            return

        for scheme_data in schemes_data:
            # Convert lists to JSON strings
            apply_steps = scheme_data.pop('apply_steps')
            required_documents = scheme_data.pop('required_documents')
            
            scheme = Scheme(
                **scheme_data,
                apply_steps=json.dumps(apply_steps),
                required_documents=json.dumps(required_documents)
            )
            
            db.session.add(scheme)
            print(f'Added: {scheme.name}')
        
        db.session.commit()
        print(f'\n✓ Successfully added {len(schemes_data)} schemes to the database!')

if __name__ == '__main__':
    seed_schemes()
