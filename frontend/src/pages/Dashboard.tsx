import React, { useState } from 'react';
import api from '../api/client';

const Dashboard: React.FC = () => {
    const [userId, setUserId] = useState('');
    const [backupCodes, setBackupCodes] = useState<string[]>([]);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleGenerateBackup = async () => {
        setError('');
        setMessage('');
        try {
            const response = await api.post('/authenticator/backup-codes/generate', {
                user_id: userId
            });
            setBackupCodes(response.data.backup_codes);
            setMessage('New backup codes generated. Save them safely!');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to generate codes');
        }
    };

    const handleDisable = async () => {
        if (!window.confirm('Are you sure you want to disable 2FA?')) return;
        setError('');
        setMessage('');
        try {
            await api.post('/authenticator/disable', {
                user_id: userId
            });
            setMessage('2FA has been disabled.');
            setBackupCodes([]);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to disable 2FA');
        }
    };

    return (
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md overflow-hidden p-6">
            <h2 className="text-2xl font-bold mb-6">User Dashboard</h2>

            <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2">User ID</label>
                <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    placeholder="Enter your User ID to manage settings"
                />
            </div>

            {message && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                    {message}
                </div>
            )}

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="border p-4 rounded bg-gray-50">
                    <h3 className="font-bold mb-2">Backup Codes</h3>
                    <p className="text-sm text-gray-600 mb-4">
                        Generate 10 single-use codes for emergency access.
                    </p>
                    <button
                        onClick={handleGenerateBackup}
                        disabled={!userId}
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
                    >
                        Generate Codes
                    </button>
                </div>

                <div className="border p-4 rounded bg-gray-50">
                    <h3 className="font-bold mb-2 text-red-600">Danger Zone</h3>
                    <p className="text-sm text-gray-600 mb-4">
                        Disable 2FA for your account.
                    </p>
                    <button
                        onClick={handleDisable}
                        disabled={!userId}
                        className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
                    >
                        Disable 2FA
                    </button>
                </div>
            </div>

            {backupCodes.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
                    <h3 className="font-bold text-yellow-800 mb-2">Your Backup Codes</h3>
                    <p className="text-sm text-yellow-700 mb-4">
                        Copy these codes now. You won't see them again!
                    </p>
                    <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                        {backupCodes.map((code, index) => (
                            <div key={index} className="bg-white p-2 border rounded text-center">
                                {code}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
