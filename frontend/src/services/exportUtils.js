import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import html2canvas from 'html2canvas';

export function exportToCSV(data, filename = 'export.csv') {
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
  XLSX.writeFile(wb, filename);
}

export async function exportToPDF(data, filename = 'export.pdf', title = 'Report', chartDataUrl = null, branding = 'South Cambridgeshire District Council') {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  let y = 15;
  // Branding and title
  doc.setFontSize(14);
  doc.text(branding, pageWidth / 2, y, { align: 'center' });
  y += 8;
  doc.setFontSize(12);
  doc.text(title, pageWidth / 2, y, { align: 'center' });
  y += 8;
  doc.setFontSize(9);
  doc.text(`Exported: ${new Date().toLocaleString()}`, 10, y);
  y += 4;
  // Chart image if provided
  if (chartDataUrl) {
    doc.addImage(chartDataUrl, 'PNG', 10, y, pageWidth - 20, 40);
    y += 45;
  }
  // Table
  if (data && data.length > 0) {
    const headers = [Object.keys(data[0])];
    const rows = data.map(row => headers[0].map(h => row[h] ?? ''));
    autoTable(doc, {
      startY: y,
      head: headers,
      body: rows,
      theme: 'grid',
      headStyles: { fillColor: [37, 99, 235] },
      styles: { fontSize: 9 },
      margin: { left: 10, right: 10 },
    });
  }
  doc.save(filename);
}

export async function exportChartAsImage(chartRef) {
  if (!chartRef || !chartRef.current) return null;
  const canvas = await html2canvas(chartRef.current, { backgroundColor: null });
  return canvas.toDataURL('image/png');
} 