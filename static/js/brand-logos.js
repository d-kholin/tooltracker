// Brand Logos Mapping
// This file contains mappings from brand names to their logo URLs
// and fallback styling for brands without logos

const BRAND_LOGOS = {
  // Major tool manufacturers with their logo URLs
  // Note: Currently using fallback text badges. Logo URLs can be added later when reliable sources are found.
  'DeWalt': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/8/89/DeWalt_Logo.svg",
    fallback: { bg: 'bg-yellow-500', text: 'text-white', border: 'border-yellow-600' }
  },
  'Milwaukee': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/d/de/Milwaukee_Logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-red-600', text: 'text-white', border: 'border-red-700' }
  },
  'Makita': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/7/71/Makita_Logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-500', text: 'text-white', border: 'border-blue-600' }
  },
  'Bosch': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/e/ee/Bosch-Logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Festool': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/4/4d/Festool.svg", // Will use fallback text badge
    fallback: { bg: 'bg-green-600', text: 'text-white', border: 'border-green-700' }
  },
  'Hilti': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/7/76/Hilti_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-red-500', text: 'text-white', border: 'border-red-600' }
  },
  'Snap-on': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/3/36/Snap-on_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-red-600', text: 'text-white', border: 'border-red-700' }
  },
  'Craftsman': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/d/dc/Craftsman_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Stanley': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/a/a7/Stanley_Hand_Tools_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Black+Decker': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/b/b9/Black%2BDecker_Logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-orange-500', text: 'text-white', border: 'border-orange-600' }
  },
  'Porter-Cable': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/7/76/Porter-Cable_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-500', text: 'text-white', border: 'border-blue-600' }
  },
  'Hitachi': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/4/4d/Hitachi_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-red-500', text: 'text-white', border: 'border-red-600' }
  },
  'Metabo': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/e/e1/Metabo_Logo_2024.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Ryobi': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/1/12/Ryobi_Logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-green-500', text: 'text-white', border: 'border-green-600' }
  },
  'Kobalt': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Husky': {
    logo: "https://en.wikipedia.org/wiki/Husky_(tool_brand)#/media/File:Husky_(tools)_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-orange-500', text: 'text-white', border: 'border-orange-600' }
  },
  'Werner': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-yellow-500', text: 'text-white', border: 'border-yellow-600' }
  },
  'Jet': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/8/8d/Jet_logo_2020.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Powermatic': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-yellow-500', text: 'text-white', border: 'border-yellow-600' }
  },
  'Delta': {
    logo: "https://en.wikipedia.org/wiki/Delta_Machinery#/media/File:Delta_Machinery_logo.jpg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Grizzly': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-red-600', text: 'text-white', border: 'border-red-700' }
  },
  'Shop Fox': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-orange-500', text: 'text-white', border: 'border-orange-600' }
  },
  'WEN': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Skil': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/f/fc/Skil_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-orange-500', text: 'text-white', border: 'border-orange-600' }
  },
  'Dremel': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/7/79/Dremel_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Bostitch': {
    logo: "upload.wikimedia.org/wikipedia/commons/c/cb/Stanley_Bostitch_Logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-red-500', text: 'text-white', border: 'border-red-600' }
  },
  'Paslode': {
    logo: "https://upload.wikimedia.org/wikipedia/en/5/57/Paslode_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'Senco': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  },
  'SawStop': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/a/a4/SawStopLogo.png", // Will use fallback text badge
    fallback: { bg: 'bg-red-600', text: 'text-white', border: 'border-red-700' }
  },
  'Mastercraft': {
    logo: "https://en.wikipedia.org/wiki/File:Mastercraft_logo.svg#/media/File:Mastercraft_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-red-500', text: 'text-white', border: 'border-red-600' }
  },
  'Rigid': {
    logo: "https://upload.wikimedia.org/wikipedia/commons/f/f0/Ridgid_logo.svg", // Will use fallback text badge
    fallback: { bg: 'bg-orange-500', text: 'text-white', border: 'border-orange-600' }
  },
  'Little Giant': {
    logo: null, // Will use fallback text badge
    fallback: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-700' }
  }
};

// Helper function to get brand info
function getBrandInfo(brandName) {
  if (!brandName) return null;
  
  // Try exact match first
  if (BRAND_LOGOS[brandName]) {
    return BRAND_LOGOS[brandName];
  }
  
  // Try case-insensitive match
  const normalizedBrand = Object.keys(BRAND_LOGOS).find(
    key => key.toLowerCase() === brandName.toLowerCase()
  );
  
  if (normalizedBrand) {
    return BRAND_LOGOS[normalizedBrand];
  }
  
  // Return default fallback for unknown brands
  return {
    logo: null,
    fallback: { bg: 'bg-gray-500', text: 'text-white', border: 'border-gray-600' }
  };
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { BRAND_LOGOS, getBrandInfo };
}
