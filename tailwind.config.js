module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
    './apps/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#27ae60',
        'primary-dark': '#219653',
        'primary-light': '#6FCF97',
        secondary: '#5A6B77',
        'secondary-dark': '#4a5b67',
        accent: '#513C6D',
        'gray-light': '#f5f5f5',
        'gray-medium': '#e0e0e0',
        'gray-dark': '#718096',
      },
      fontFamily: {
        'poppins': ['"Poppins"', 'sans-serif'],
        'inter': ['"Inter"', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 