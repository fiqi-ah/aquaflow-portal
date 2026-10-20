import { useEffect, useState } from 'react';
import api from '../api';
import { Download, CheckCircle, Clock, AlertTriangle, Package } from 'lucide-react';

export default function AdminDashboard() {
    const [invoices, setInvoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);

    const fetchPending = async () => {
        try {
            const res = await api.get('/invoices/pending');
            setInvoices(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPending();
    }, []);

    const handleApprove = async (id) => {
        if (!confirm("Are you sure you want to approve this delivery record?")) return;

        try {
            await api.patch(`/invoices/${id}/approve`);
            setInvoices(prev => prev.filter(inv => inv.id !== id));
        } catch (err) {
            alert("Error approving invoice");
        }
    };

    const handleExport = async () => {
        if (invoices.length === 0) {
            alert("No approved invoices ready for export.");
            return;
        }

        setExporting(true);
        try {
            const res = await api.get('/export/iif', { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `qb_delivery_import_${new Date().toISOString().slice(0, 10)}.iif`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            fetchPending();
        } catch (err) {
            alert("Export failed. Ensure there are APPROVED items.");
        } finally {
            setExporting(false);
        }
    };

    if (loading) return <div className="text-center py-10">Loading dashboard...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Delivery Approval Queue</h2>
                    <p className="mt-1 text-sm text-gray-500">Review recorded deliveries before exporting to QuickBooks.</p>
                </div>
                <button
                    onClick={handleExport}
                    disabled={exporting || invoices.length === 0}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Download className="h-4 w-4 mr-2" />
                    {exporting ? 'Generating...' : 'Export Approved to QB'}
                </button>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                    {invoices.length === 0 ? (
                        <li className="px-6 py-10 text-center text-gray-500">
                            <Clock className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                            No pending approvals. All clear!
                        </li>
                    ) : (
                        invoices.map((inv) => (
                            <li key={inv.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                                <div className="flex items-center justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <Package className="h-5 w-5 text-blue-500" />
                                            <p className="text-sm font-medium text-gray-900 truncate">
                                                {inv.customer_name} <span className="text-gray-400 font-normal">(ID: {inv.customer_id})</span>
                                            </p>
                                        </div>
                                        <p className="mt-1 text-sm text-gray-500 truncate">
                                            📍 {inv.customer_address}
                                        </p>
                                        <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
                                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-semibold">
                                                {inv.bottles_delivered} Bottles
                                            </span>
                                            <span>Date: {new Date(inv.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>

                                    <div className="ml-4 flex-shrink-0 flex flex-col items-end gap-2">
                                        <button
                                            onClick={() => handleApprove(inv.id)}
                                            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-full text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                        >
                                            <CheckCircle className="h-3 w-3 mr-1" />
                                            Approve
                                        </button>
                                    </div>
                                </div>
                            </li>
                        ))
                    )}
                </ul>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div className="flex">
                    <div className="flex-shrink-0">
                        <AlertTriangle className="h-5 w-5 text-yellow-400" aria-hidden="true" />
                    </div>
                    <div className="ml-3">
                        <p className="text-sm text-yellow-700">
                            <strong>Note:</strong> This export assumes a fixed rate per bottle defined in the backend. Adjust pricing logic in `qb_export.py` if rates vary.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}