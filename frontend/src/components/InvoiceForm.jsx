import { useState } from 'react';
import api from '../api';
import { Send, AlertCircle, CheckCircle, Truck, MapPin, Hash } from 'lucide-react';

export default function InvoiceForm() {
    const [formData, setFormData] = useState({
        customer_name: '',
        customer_id: '',
        customer_address: '',
        bottles_delivered: ''
    });
    const [status, setStatus] = useState({ type: null, message: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setStatus({ type: null, message: '' });

        try {
            const payload = {
                ...formData,
                bottles_delivered: parseInt(formData.bottles_delivered, 10)
            };

            await api.post('/invoices/', payload);

            setStatus({ type: 'success', message: 'Delivery record submitted successfully!' });
            setFormData({ customer_name: '', customer_id: '', customer_address: '', bottles_delivered: '' });
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to submit entry.';
            setStatus({ type: 'error', message: msg });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                <h3 className="text-lg leading-6 font-medium text-gray-900">New Delivery Entry</h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">Record water bottle deliveries.</p>
            </div>

            <div className="px-4 py-5 sm:p-6">
                {status.message && (
                    <div className={`mb-4 p-3 rounded-md flex items-center gap-2 ${status.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                        }`}>
                        {status.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
                        {status.message}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">

                    {/* Customer Name */}
                    <div className="sm:col-span-6">
                        <label htmlFor="customer_name" className="block text-sm font-medium text-gray-700">Customer Name</label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Truck className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                type="text" name="customer_name" id="customer_name" required
                                value={formData.customer_name} onChange={handleChange}
                                className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 pr-3 py-2 sm:text-sm border-gray-300 rounded-md"
                                placeholder="e.g., John Smith"
                            />
                        </div>
                    </div>

                    {/* Customer ID */}
                    <div className="sm:col-span-3">
                        <label htmlFor="customer_id" className="block text-sm font-medium text-gray-700">Customer ID</label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Hash className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                type="text" name="customer_id" id="customer_id" required
                                value={formData.customer_id} onChange={handleChange}
                                className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 pr-3 py-2 sm:text-sm border-gray-300 rounded-md"
                                placeholder="e.g., CUST-001"
                            />
                        </div>
                    </div>

                    {/* Bottles Delivered */}
                    <div className="sm:col-span-3">
                        <label htmlFor="bottles_delivered" className="block text-sm font-medium text-gray-700">No. of Bottles</label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <input
                                type="number" min="1" step="1" name="bottles_delivered" id="bottles_delivered" required
                                value={formData.bottles_delivered} onChange={handleChange}
                                className="focus:ring-blue-500 focus:border-blue-500 block w-full pr-3 py-2 sm:text-sm border-gray-300 rounded-md"
                                placeholder="0"
                            />
                        </div>
                    </div>

                    {/* Address */}
                    <div className="sm:col-span-6">
                        <label htmlFor="customer_address" className="block text-sm font-medium text-gray-700">Delivery Address</label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <MapPin className="h-5 w-5 text-gray-400" />
                            </div>
                            <textarea
                                id="customer_address" name="customer_address" rows="3" required
                                value={formData.customer_address} onChange={handleChange}
                                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 pr-3 py-2 sm:text-sm border-gray-300 rounded-md"
                                placeholder="Street, City, Zip Code"
                            ></textarea>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="sm:col-span-6">
                        <button
                            type="submit" disabled={isSubmitting}
                            className="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all"
                        >
                            <Send className="h-4 w-4 mr-2" />
                            {isSubmitting ? 'Submitting...' : 'Record Delivery'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}