import React, { useState, useEffect } from 'react';
import api from '../api/client';

const VerifyPage: React.FC = () => {
    const [userId, setUserId] = useState('');
    const [code, setCode] = useState('');
    const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');
    const [countdown, setCountdown] = useState(30);

    useEffect(() => {
        const timer = setInterval(() => {
            setCountdown((prev) => (prev > 0 ? prev - 1 : 30));
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus('idle');
        setMessage('');
        try {
            const response = await api.post('/authenticator/verify', {
                user_id: userId,
                code: code
            });
            if (response.data.verified) {
                setStatus('success');
                setMessage('Verification Successful!');
            } else {
                setStatus('error');
                setMessage(response.data.error || 'Verification Failed');
            }
        } catch (err: any) {
            setStatus('error');
            setMessage(err.response?.data?.detail || 'Verification Failed');
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-md overflow-hidden p-6">
            <h2 className="text-2xl font-bold mb-6 text-center">Verify 2FA</h2>

            <div className="mb-6 text-center">
                <div className="text-4xl font-mono font-bold text-gray-300 mb-2">
                    {countdown}s
                </div>
                <p className="text-xs text-gray-500">Next code rotation (approx)</p>
            </div>

            <form onSubmit={handleVerify}>
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2">User ID</label>
                    <input
                        type="text"
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        required
                    />
                </div>
                <div className="mb-6">
                    <label className="block text-gray-700 text-sm font-bold mb-2">TOTP Code</label>
                    <input
                        type="text"
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-center text-xl tracking-widest"
                        placeholder="000000"
                        maxLength={6}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                    Verify
                </button>
            </form>

            {status === 'success' && (
                <div className="mt-4 p-4 bg-green-100 text-green-700 rounded text-center font-bold">
                    {message}
                </div>
            )}

            {status === 'error' && (
                <div className="mt-4 p-4 bg-red-100 text-red-700 rounded text-center">
                    {message}
                </div>
            )}
        </div>
    );
};

export default VerifyPage;
