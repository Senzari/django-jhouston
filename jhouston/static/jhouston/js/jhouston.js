(function() {
  var prevOnError = window.onerror;
  window.onerror = function (errorMsg, url, lineNumber) {
	  if (typeof(jQuery) != 'undefined') {
  	    jQuery.ajax({
  	      url: '/jserror/',
  			  type: 'POST',
  			  data: {
  			      message: errorMsg,
  			      line_number: lineNumber,
  			      url: url
  			  }
  			});
  	}
  	if (prevOnError) {
  	    return prevOnError(errorMsg, url, lineNumber);
  	}
  	return false;
  }
  
  // a logger for logging front end events. extra must be a javascript object
  // serializable to json
  // usage:
  // window.jhouston_logger('info', 'this value is wrong', {value: 'wrong'});
  window.jhouston_logger = function(level, message, extra) {
    extra = JSON.stringify(extra);
    jQuery.ajax({
      url: '/jslog/',
		  type: 'POST',
		  data: {
		      message: message,
		      log_level: level,
		      extra: extra,
		  }
		});
		
		// try printing to the console too.
		try {
		  console.log(level, message, extra);
		}
		catch (error) {}
  } 
})();