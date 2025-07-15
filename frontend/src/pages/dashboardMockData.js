// South Cambridgeshire NNDR Dashboard Mock Data (2025/26 realistic)

export const summaryCards = [
  { label: 'Total Business Properties', value: 4350 },
  { label: 'Total Rateable Value', value: '£132,000,000' },
  { label: 'Net NNDR Income (2025/26)', value: '£51,200,000' },
  { label: 'Average Rateable Value', value: '£30,345' },
  { label: '% in Receipt of Relief', value: '38%' },
  { label: 'Top Sectors', value: 'Industrial, Office, Retail' },
];

export const sectorBreakdown = [
  { sector: 'Retail', properties: 950, medianRV: 22000, totalRV: 21000000, percentWithRelief: 55, notes: 'High St, villages' },
  { sector: 'Office', properties: 1200, medianRV: 40000, totalRV: 48000000, percentWithRelief: 30, notes: 'Cambourne, parks' },
  { sector: 'Industrial', properties: 1400, medianRV: 60000, totalRV: 54000000, percentWithRelief: 25, notes: 'Science/Ind. parks' },
  { sector: 'Hospitality', properties: 350, medianRV: 30000, totalRV: 10500000, percentWithRelief: 60, notes: 'Pubs, hotels, cafes' },
  { sector: 'Other', properties: 450, medianRV: 18000, totalRV: 8100000, percentWithRelief: 40, notes: 'Health, leisure, etc' },
];

export const topRatepayers = [
  { name: 'Cambridge Science Park', sector: 'Industrial', rv: 250000, address: 'Milton Rd, CB4', reliefs: 'None' },
  { name: 'Cambourne Business Centre', sector: 'Office', rv: 180000, address: 'Cambourne, CB23', reliefs: 'None' },
  { name: 'Tesco Superstore', sector: 'Retail', rv: 120000, address: 'Bar Hill, CB23', reliefs: 'RHL 40%' },
  { name: 'Addenbrooke’s Hospital', sector: 'Other', rv: 110000, address: 'Hills Rd, CB2', reliefs: 'Charitable' },
  { name: 'Sainsbury’s', sector: 'Retail', rv: 95000, address: 'Cambridge Rd, CB22', reliefs: 'RHL 40%' },
  { name: 'AstraZeneca', sector: 'Industrial', rv: 90000, address: 'Granta Park, CB21', reliefs: 'None' },
  { name: 'Premier Inn', sector: 'Hospitality', rv: 80000, address: 'Cambridge Rd, CB22', reliefs: 'RHL 40%' },
  { name: 'John Lewis', sector: 'Retail', rv: 75000, address: 'Cambridge, CB2', reliefs: 'RHL 40%' },
  { name: 'Cambridge Leisure', sector: 'Other', rv: 70000, address: 'Clifton Way, CB1', reliefs: 'None' },
  { name: 'Local Pub Group', sector: 'Hospitality', rv: 65000, address: 'Various', reliefs: 'RHL 40%' },
];

export const reliefDistribution = [
  { type: 'Retail, Hospitality, Leisure', percent: 40 },
  { type: 'Small Business', percent: 30 },
  { type: 'Charitable', percent: 15 },
  { type: 'Empty Property', percent: 10 },
  { type: 'Other', percent: 5 },
];

export const mapPoints = [
  { name: 'Cambridge Science Park', lat: 52.235, lng: 0.138, sector: 'Industrial', rv: 250000, relief: 'None' },
  { name: 'Cambourne Business Centre', lat: 52.223, lng: -0.070, sector: 'Office', rv: 180000, relief: 'None' },
  { name: 'Tesco Superstore', lat: 52.253, lng: 0.022, sector: 'Retail', rv: 120000, relief: 'RHL 40%' },
  { name: 'Addenbrooke’s Hospital', lat: 52.176, lng: 0.137, sector: 'Other', rv: 110000, relief: 'Charitable' },
  { name: 'Sainsbury’s', lat: 52.150, lng: 0.120, sector: 'Retail', rv: 95000, relief: 'RHL 40%' },
  { name: 'AstraZeneca', lat: 52.140, lng: 0.210, sector: 'Industrial', rv: 90000, relief: 'None' },
  { name: 'Premier Inn', lat: 52.200, lng: 0.110, sector: 'Hospitality', rv: 80000, relief: 'RHL 40%' },
  { name: 'John Lewis', lat: 52.205, lng: 0.119, sector: 'Retail', rv: 75000, relief: 'RHL 40%' },
  { name: 'Cambridge Leisure', lat: 52.194, lng: 0.137, sector: 'Other', rv: 70000, relief: 'None' },
  { name: 'Local Pub Group', lat: 52.210, lng: 0.130, sector: 'Hospitality', rv: 65000, relief: 'RHL 40%' },
  // Add more points for clusters in Bar Hill, Sawston, A14/A428, etc.
  { name: 'Bar Hill Retail Park', lat: 52.255, lng: 0.022, sector: 'Retail', rv: 60000, relief: 'RHL 40%' },
  { name: 'Sawston Industrial Estate', lat: 52.120, lng: 0.170, sector: 'Industrial', rv: 55000, relief: 'None' },
  { name: 'Granta Park', lat: 52.080, lng: 0.190, sector: 'Industrial', rv: 85000, relief: 'None' },
  { name: 'Cambourne Retail', lat: 52.220, lng: -0.070, sector: 'Retail', rv: 40000, relief: 'RHL 40%' },
  { name: 'Village Pub', lat: 52.180, lng: 0.100, sector: 'Hospitality', rv: 25000, relief: 'RHL 40%' },
];

export const nndrTrends = [
  { year: 2019, netIncome: 44200000 },
  { year: 2020, netIncome: 43800000 },
  { year: 2021, netIncome: 45100000 },
  { year: 2022, netIncome: 47300000 },
  { year: 2023, netIncome: 49000000 },
  { year: 2024, netIncome: 50500000 },
  { year: 2025, netIncome: 51200000 },
]; 