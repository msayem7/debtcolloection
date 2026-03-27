
const monthNames = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

export function formatDateTime (dateString) {
  if (!dateString) return 'N/A'
  return formatDate(dateString) // Or implement a specific date-time formatter
}

export function formatDate(dateString) {
  
  // console.log("VUE_APP_DATE_FORMAT=", process.env.VUE_APP_DATE_FORMAT, "VUE_APP_DIGITS_AFTER_DECIMAL=", 
  //   process.env.VUE_APP_DIGITS_AFTER_DECIMAL, "VUE_APP_DISPLAY_SYSTEM=", process.env.VUE_APP_DISPLAY_SYSTEM)

  const date = new Date(dateString);
  if (isNaN(date)) {
    return "Invalid Date";
  }

  const options = {
    timeZone: 'Asia/Dhaka',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };
  
  //'return date.toLocaleString('en-IN', options);
  const parts= date.toISOString().split('T');
  return parts[0];

}

export function ServerDateFormat(dateString){

  return this.formatDateToISO(new Date(dateString));

}
  
function ISODatePart(isoString) {
  if (typeof isoString !== 'string') {
    return "Invalid Input";
  }

  const parts = isoString.split('T');
  if (parts.length < 1) {
    return "Invalid ISO String";
  }


  return parts[0];
}

 

export function parseDate(dateString) {
  // Handle both YYYY-MM-DD (from date inputs) and dd-MMM-yyyy formats

  // console.log("parseDate(dateString)", dateString)
  const parts = dateString.split(/[-/]/)
  
  // console.log("parts :", parts, "parts.length :", parts.length)
  if (parts.length === 3) {
    // Try ISO format first
    if (parts[0].length === 4) {
      return new Date(dateString)
    }
    
    // Handle dd-MMM-yyyy format
    const day = parseInt(parts[0], 10)
    const month = monthNames.indexOf(parts[1])
    const year = parseInt(parts[2], 10)
    
    // console.log("day :", day, "month :", month, "year :", year)
    
    if (month > -1 && !isNaN(day) && !isNaN(year)) {      
      // console.log("New date :", new Date(year, month, day))
      return new Date(year, month, day)
    }
  }

  return new Date()
}


export function parseNumber(formattedValue) {
  // Convert to string if not already
  const stringValue = String(formattedValue || '');
  
  // Clean numeric string
  const numericString = stringValue
    .replace(/[^0-9.]/g, '')
    .replace(/\.(?=.*\.)/g, '');

  return parseFloat(numericString) || 0;
}

export function formatNumber(value, decimals = 0) { //decimals = process.env.VUE_APP_DIGITS_AFTER_DECIMAL is not working here. need to investigate why
    // Ensure numeric value
  const number = typeof value === 'number' ? value : parseFloat(value) || 0;
  // console.log("typeof value :", typeof value, "number :", number)
  return number.toLocaleString( process.env.VUE_APP_DISPLAY_SYSTEM,{
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
} 