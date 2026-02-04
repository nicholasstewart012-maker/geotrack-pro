/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                ios: {
                    bg: '#000000',
                    card: 'rgba(28, 28, 30, 0.7)',
                    text: '#FFFFFF',
                    secondary: '#8E8E93',
                    blue: '#0A84FF',
                    green: '#30D158',
                    red: '#FF453A',
                    amber: '#FFD60A',
                }
            },
            fontFamily: {
                sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
            },
            borderRadius: {
                '2xl': '24px',
                '3xl': '32px',
                '4xl': '40px',
            },
            backdropBlur: {
                'acrylic': '40px',
            },
            backgroundImage: {
                'premium': "url('/bg-premium.png')",
                'ios-gradient': 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 100%)',
            },
            boxShadow: {
                'ios-premium': '0 10px 40px rgba(0, 0, 0, 0.5)',
            }
        },
    },
    plugins: [],
}
