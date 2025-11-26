import React, { useState } from 'react';
import api from '../api/client';
import { useNavigate } from 'react-router-dom';

const SetupWizard: React.FC = () => {
    const [step, setStep] = useState(1);
    const [userId, setUserId] = useState<string>(crypto.randomUUID());
    const [displayName, setDisplayName] = useState('');
    const [qrSvg, setQrSvg] = useState('');
    const [secret, setSecret] = useState('');
    const [provisionToken, setProvisionToken] = useState('');
    const [verifyCode, setVerifyCode] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleProvision = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            const response = await api.post('/authenticator/provision', {
                user_id: userId,
                display_name: displayName,
                issuer: 'MyCompany'
            });
            setQrSvg(response.data.qr_svg);
            setSecret(response.data.secret_base32);
            setProvisionToken(response.data.provision_token);
            setStep(2);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Provisioning failed');
        }
    };

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            await api.post('/authenticator/verify-setup', {
                provision_token: provisionToken,
                code: verifyCode
            });
            setStep(3);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Verification failed');
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-md overflow-hidden p-6">
            <h2 className="text-2xl font-bold mb-6 text-center">Setup 2FA</h2>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            {step === 1 && (
                <form onSubmit={handleProvision}>
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
                        <label className="block text-gray-700 text-sm font-bold mb-2">Display Name</label>
                        <input
                            type="text"
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    >
                        Start Setup
                    </button>
                </form>
            )}

            {step === 2 && (
                <div className="text-center">
                    <p className="mb-4">Scan this QR code with your authenticator app:</p>
                    <div
                        className="mb-4 flex justify-center"
                        dangerouslySetInnerHTML={{ __html: qrSvg }}
                    />
                    <p className="text-sm text-gray-600 mb-4">
                        Or enter this secret manually: <br />
                        <span className="font-mono font-bold select-all">{secret}</span>
                    </p>

                    <form onSubmit={handleVerify}>
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-bold mb-2">Verification Code</label>
                            <input
                                type="text"
                                value={verifyCode}
                                onChange={(e) => setVerifyCode(e.target.value)}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-center text-xl tracking-widest"
                                placeholder="000000"
                                maxLength={6}
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            className="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        >
                            Verify & Activate
                        </button>
                    </form>
                </div>
            )}

            {step === 3 && (
                <div className="text-center">
                    <div className="text-green-500 text-5xl mb-4">✓</div>
                    <h3 className="text-xl font-bold mb-2">Setup Complete!</h3>
                    <p className="mb-6">Your authenticator is now active.</p>
                    <button
                        onClick={() => navigate('/')}
                        className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    >
                        Go to Verification Demo
                    </button>
                </div>
            )}
        </div>
    );
};

export default SetupWizard;
