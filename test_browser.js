// Test script to check browser-side API access
const testBrowserAPI = async () => {
    console.log('Testing browser-side API access...');

    try {
        // Test the API endpoint that the map uses
        const response = await fetch('/api/soldiers/');

        if (!response.ok) {
            console.error(`API Error: HTTP ${response.status} - ${response.statusText}`);
            console.log('Response headers:', Object.fromEntries([...response.headers]));
            return false;
        }

        const data = await response.json();
        console.log('API Response:', data);
        console.log('✅ API accessible from browser');
        return true;

    } catch (error) {
        console.error('❌ Browser API Error:', error);
        console.log('This suggests a CORS issue or network problem');
        return false;
    }
};

// Run the test
testBrowserAPI();