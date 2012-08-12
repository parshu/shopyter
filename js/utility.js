function execURL(url, asynchronous){
		var ajaxRequest;  // The variable that makes Ajax possible!
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");
					return false;
				}
			}
		}
		
		ajaxRequest.open("GET", url, asynchronous); 
		ajaxRequest.send(null); 
		
	}
	
	  function sortCurrentDeals(selection, username)
    {
    	var ajaxDisplay = document.getElementById("filtersholder");
		var qid = ajaxDisplay.getAttribute("qid");
		var values = selection.split(",")
		renderDealResults('/getdeals/' + username + '/' + qid + '/1/200/9/' + values[0] + '/' + values[1] + '/getdeals.html','dealresultsdiv');
    }
    
    function renderProgressBar()
    {
    	var ajaxDisplay = document.getElementById("dealresultsdiv");
		ajaxDisplay.innerHTML = '<div class="progress progress-success" style="padding-top:30px;padding-left:30px;padding-right:30px;"><div class="bar" style="float: left; width: 0%; " data-percentage="100"></div></div>';
		
    
    }
    
    
    function renderLocationEdit() {
    	var html = '<input type="text" id="address" class="input-medium" style="width:118px;" placeholder="loc..." required>&nbsp;<button type="submit" class="btn btn-primary">Save</button>';
    	var ajaxDisplay = document.getElementById("userlocation");
    	ajaxDisplay.innerHTML = html;
    	ajaxDisplay = document.getElementById("editlink");
		ajaxDisplay.innerHTML = "";
    }
    
    
     
    function saveLocation(address, username) {
    	var geocoder = new google.maps.Geocoder();
    	geocoder.geocode( { 'address': address}, function(results, status) {
			  if (status == google.maps.GeocoderStatus.OK) {
				var city = results[0].address_components[0].short_name;
				var state = results[0].address_components[2].short_name;
				
				var lat = results[0].geometry.location.lat();
				var lng = results[0].geometry.location.lng();
				execURL('/updatelocation/' + username + '/' + city + '/' + state + '/' + lat + '/' + lng , true);
				var ajaxDisplay = document.getElementById("userlocation");
				ajaxDisplay.innerHTML = city + ", " + state;
				ajaxDisplay = document.getElementById("editlink");
				ajaxDisplay.innerHTML = "edit";
				
				
			  } else {
				alert("Geocode was not successful for the following reason: " + status);
			  }
			});
    
    }

	function doAnimation() {
			
			
			
			
			 $('.progress .bar').each(function() {
            var me = $(this);
            var perc = me.attr("data-percentage");
			
            //TODO: left and right text handling

            var current_perc = 0;

            var progress = setInterval(function() {
                if (current_perc>=perc) {
                    clearInterval(progress);
                } else {
                    current_perc +=5;
                    me.css('width', (current_perc)+'%');
                }
				
				var sourcesite = ['Amazon', 'Ebay','Craigslist', 'Walmart', 'Web'];
				var index = Math.floor(current_perc / 20);
                me.text('Scouring ' + sourcesite[index]);

            }, 200);

        	});
			
			
			

			

	
		}
		
		
	function bookmark(title, url) 
    {
       

        if (document.all)// Check if the browser is Internet Explorer
            window.external.AddFavorite(url, title);

        else if (window.sidebar) //If the given browser is Mozilla Firefox
            window.sidebar.addPanel(title, url, "");

        else if (window.opera && window.print) //If the given browser is Opera
        {
            var bookmark_element = document.createElement('a');
            bookmark_element.setAttribute('href', url);
            bookmark_element.setAttribute('title', title);
            bookmark_element.setAttribute('rel', 'sidebar');
            bookmark_element.click();
        }
    }

 function renderTextInDiv(text, divname){

		var ajaxDisplay = document.getElementById(divname);
		ajaxDisplay.innerHTML = text;
		
		
	}
    
    
    function updateDeals(username, qid){
		var ajaxRequest;  // The variable that makes Ajax possible!
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");
					return false;
				}
			}
		}
		// Create a function that will receive data sent from the server
		ajaxRequest.onreadystatechange = function(){
			if(ajaxRequest.readyState == 4){
				
				
				var ajaxDisplay = document.getElementById("newdealalert");
				
				ajaxDisplay.innerHTML = ajaxRequest.responseText;
			}
		}
		ajaxRequest.open("GET", "/dealsupdate/" + username + "/" + qid, true); 
		ajaxRequest.send(null); 
		
	}
    
    
    
    function renderURLinDiv(url, divname, asynchronous){
		var ajaxRequest;  // The variable that makes Ajax possible!
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");
					return false;
				}
			}
		}
		// Create a function that will receive data sent from the server
		ajaxRequest.onreadystatechange = function(){
			if(ajaxRequest.readyState == 4){
				var ajaxDisplay = document.getElementById(divname);
				ajaxDisplay.innerHTML = ajaxRequest.responseText;
			}
		}
		ajaxRequest.open("GET", url, asynchronous); 
		ajaxRequest.send(null); 
		
	}
	function indicateSaved(url, divname, asynchronous){
		var ajaxRequest;  // The variable that makes Ajax possible!
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");
					return false;
				}
			}
		}
		// Create a function that will receive data sent from the server
		ajaxRequest.onreadystatechange = function(){
			if(ajaxRequest.readyState == 4){
				var ajaxDisplay = document.getElementById(divname);
				ajaxDisplay.innerHTML = ajaxRequest.responseText;
				ajaxDisplay.setAttribute("style","background-color:lightgreen; background-image: -moz-linear-gradient(center top , lightgreen, lightgreen);");
			}
		}
		ajaxRequest.open("GET", url, asynchronous); 
		ajaxRequest.send(null); 
		
	}
	
	function setMapQueryId(qid)
	{
		ajaxDisplay = document.getElementById("secondcol");
		ajaxDisplay.setAttribute("qid",qid);
	
	}
	
	function clickCurrentQuery()
	{
		
		var filtersele = document.getElementById("filtersholder");
		var lpid = filtersele.getAttribute("loopid");
		var linkele = document.getElementById(lpid);
		linkele.click();	
	
	}
	
	 function saveTag(newtag, username, qid) {
      	    
      	  
	      //execURL('/updatequeryfilters/' + qid + '/' + 'tag|' + newtag, false);
	      execURL('/savetag/' + username + '/' + qid + '/' + newtag,true);
	      
	      clickCurrentQuery();
	      //updateDeals(username,qid);

	      

      }
      
	function saveDeal(dealid, username)
    {
    	indicateSaved('/savedeal/' + dealid + '/' + username, dealid, true);
    }
    function unsaveDeal(dealid, username)
    {
    	renderURLinDiv('/unsavedeal/' + dealid + '/' + username, 'tn' + dealid, true);
    }
    
    function clearOldPoll()
    {
    	if(timerId != "") {
    		clearInterval(timerId);
    	}
    
    }
    
    function beginNewDealPoll(username, qid) 
    {
    	/*timerId = setInterval( function(){
    		//checkNewDeals('/checknewdeals/' + username + '/' + qid);
    	},5000);*/
    
    }
	
	function highlightQuery(id) {
		
		var activeele = document.getElementById("activequerytr");
		if(activeele != null) {
			activeele.removeAttribute("style");
			var realid = activeele.getAttribute("realid");
			activeele.setAttribute("id", realid);
		}
		var clickedele = document.getElementById(id);
		clickedele.setAttribute("id", "activequerytr");
		clickedele.setAttribute("style", "background:lightgrey;");
		
	}
	
	 //noOfQueries - unused as of now
	//queryBoxDivname - Name of the  query box div
	//queryBoxURL - URL that needs to be requested for the query box html. This is rendered in queryBoxDivname
    
    function renderQueryBox(queryBoxURL, queryBoxDivname, noOfQueries){
		var ajaxRequest;  // The variable that makes Ajax possible!
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");
					return false;
				}
			}
		}
		// Create a function that will receive data sent from the server
		ajaxRequest.onreadystatechange = function(){
			if(ajaxRequest.readyState == 4){
				var ajaxDisplay = document.getElementById(queryBoxDivname);
				ajaxDisplay.innerHTML = ajaxRequest.responseText;
			}
		}
		ajaxRequest.open("GET", queryBoxURL, false); // false: synchronous call to eliminate weird UI behavior
		ajaxRequest.send(null); 
		
	}
    
    //noOfQueries - unused as of now
	//queryIndex - Index of the selected query. Used for highlighting
	//dealResultsDivname - Name of the  deal results div
	//dealResultsURL - URL that needs to be requested for the deal results html. This is rendered in queryBoxDivname
	
	function renderDealResults(dealResultsURL, dealResultsDivname){
	
		var sortby = document.getElementById('sortorder').options[document.getElementById('sortorder').selectedIndex].value;
		sortby = sortby.replace(",","/");
		dealResultsURL = dealResultsURL.replace("sortbyfield",sortby);
		var ajaxRequest;  // The variable that makes Ajax possible!
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");

					return false;
				}
			}
		}
		// function that will receive data sent from the server
		ajaxRequest.onreadystatechange = function(){
			if(ajaxRequest.readyState == 4){
				var ajaxDisplay = document.getElementById(dealResultsDivname);
				ajaxDisplay.innerHTML = ajaxRequest.responseText;
			}
		}
		ajaxRequest.open("GET", dealResultsURL, false); // false: synchronous call to eliminate weird UI behavior
		ajaxRequest.send(null); 
		
		
	}
	
	function renderMapResults(dealResultsURL, dealResultsDivname, height){
		
		var ajaxDisplay = document.getElementById(dealResultsDivname);
		ajaxDisplay.innerHTML = '<iframe width="100%" height="' + height + '" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="' + dealResultsURL  + '"></iframe>';
	
		
		
	}
	
	// Function to validate that a typed char is a number or . (used to validate entry in $box
	function isNumberKey(evt)
    {
          var charCode = (evt.which) ? evt.which : event.keyCode
          if (charCode > 31 
            && (charCode < 48 || charCode > 57))
             return false;

          return true;
    }

	 function recordOutboundLink(link) {
    		_gaq.push(['_trackEvent', 'deals', 'click', 'knoponpage']);
    		setTimeout('document.location = "' + link.href + '"', 100);
  	  } 
     
	
	function makeBigMapChanges(username)
	{
		/*var ajaxDisplay = document.getElementById("filtersdiv");
		var filtercontent = ajaxDisplay.innerHTML;
		ajaxDisplay = document.getElementById("tempfiltersdiv");
		ajaxDisplay.innerHTML = filtercontent;*/
		var ajaxDisplay = document.getElementById("thirdcol");
		ajaxDisplay.setAttribute("class","span0");
		ajaxDisplay = document.getElementById("secondcol");
		ajaxDisplay.setAttribute("class","span9");
		var qid = ajaxDisplay.getAttribute("qid");
		renderMapResults('/getdeals/' + username + '/' + qid + '/1/200/12/nosort/nosorttype/getmap.html','localmaps', 1000);
		ajaxDisplay = document.getElementById("thirdcol");
		ajaxDisplay.setAttribute("selectedmap","localmaps");
	}
	
	
	
  
    
    
	
	function revertBigMapChanges(username, mapheight)
	{
		
		/*ajaxDisplay = document.getElementById("tempfiltersdiv");
		ajaxDisplay.innerHTML = "";*/
		var ajaxDisplay = document.getElementById("thirdcol");
		ajaxDisplay.setAttribute("class","span3");
		ajaxDisplay = document.getElementById("secondcol");
		ajaxDisplay.setAttribute("class","span6");
		var qid = ajaxDisplay.getAttribute("qid");
		renderMapResults('/getdeals/' + username + '/' + qid + '/1/200/10/nosort/nosorttype/getmap.html','mapresultsdiv', mapheight);
		ajaxDisplay = document.getElementById("thirdcol");
		ajaxDisplay.setAttribute("selectedmap","mapresultsdiv");
	}
	
	
	
	
	function renderSelectedMap(username, qid, mapheight)
	{
		var ajaxDisplay = document.getElementById("thirdcol");
		var selmap = ajaxDisplay.getAttribute("selectedmap");
		if(selmap == 'localmaps') {
			renderMapResults('/getdeals/' + username + '/' + qid + '/1/200/12/nosort/nosorttype/getmap.html','localmaps',  1000);
		} else {
			renderMapResults('/getdeals/' + username + '/' + qid + '/1/200/10/nosort/nosorttype/getmap.html','mapresultsdiv',  mapheight);
		}
	
	}
	
	  
    
	
	function renderPriceSlider(loopid, username) {
		var ajaxDisplay = document.getElementById(loopid);
		var pricemin = parseInt(ajaxDisplay.getAttribute("pmn"));
		var pricemax = parseInt(ajaxDisplay.getAttribute("pmx"));
		var pricelow = parseInt(ajaxDisplay.getAttribute("pl"));
		var pricehigh = parseInt(ajaxDisplay.getAttribute("ph"));
		$(function() {
			$( "#slider-range" ).slider({
				range: true,
				min: pricemin,
				max: pricemax,
				values: [ pricelow, pricehigh ],
				slide: function( event, ui ) {
					$( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
					
				},
				stop: function( event, ui ) {
					//ui.values[0] & ui.values[1]
					var ele = document.getElementById("filtersholder");
					var qid = ele.getAttribute("qid");
					execURL('/updatequerypricerange/' + qid + '/' + ui.values[0] + '/' + ui.values[1], false);
					var lpid = ele.getAttribute("loopid");
					var linkele = document.getElementById(lpid);
					linkele.setAttribute("pl",ui.values[0]);
					linkele.setAttribute("ph",ui.values[1]);
					linkele.click();
					execURL("/updatemetrics/" + username + "/increment/{\"filtersused\":1}",true);
					updateDeals(username,qid);
					
										
					
				}
			});
			$( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
				" - $" + $( "#slider-range" ).slider( "values", 1 ) );
		});
	
	}
	
	function renderDaysSlider(loopid, username) {
		var ajaxDisplay = document.getElementById(loopid);
		var days = parseInt(ajaxDisplay.getAttribute("df"));
		$(function() {
			$( "#slider-range-min" ).slider({
				range: "min",
				value: days,
				min: 1,
				max: 21,
				slide: function( event, ui ) {
					$( "#days" ).val( ui.value + " days ago" );
				},
				stop: function( event, ui ) {
					var ele = document.getElementById("filtersholder");
					var qid = ele.getAttribute("qid");
					execURL('/updatequerydays/' + qid + '/' + ui.value, false);
					var lpid = ele.getAttribute("loopid");
					var linkele = document.getElementById(lpid);
					linkele.setAttribute("df",ui.value);
					linkele.click();
					execURL("/updatemetrics/" + username + "/increment/{\"filtersused\":1}",true);											
					
				}
			});
			$( "#days" ).val( $( "#slider-range-min" ).slider( "value" ) + " days ago");
		});
	}
	
	function saveFilter(queryid, eleid, filtername, username) {
		var ele = document.getElementById(eleid);
		var classval = ele.getAttribute("class");
		var filtersele = document.getElementById("filtersholder");
		var selectedbuttons = filtersele.getAttribute("selectedbuttons");
		if(classval == "btn") {
			selectedbuttons = selectedbuttons + "," + filtername;
		}
		else {
			selectedbuttons = selectedbuttons.replace("," + filtername, "");
		}
		filtersele.setAttribute("selectedbuttons", selectedbuttons);
		if(selectedbuttons == "") {
			selectedbuttons = "-1";
		}
		execURL('/updatequeryfilters/' + queryid + '/' + selectedbuttons, false);
		var lpid = filtersele.getAttribute("loopid");
		var linkele = document.getElementById(lpid);
		linkele.click();
		updateDeals(username,queryid);
		
	
	}
    
       
  	//url - URL containing information to delete a query
	// highlightIndex - highlighted query
	// keyword/dollarlimit pair used as primary key contained in url
	
	  function addQuery(url, username){
  
    	
    	execURL("/updatemetrics/" + username + "/increment/{\"queryadd\":1}",true);
		var ajaxRequest;  // The variable that makes Ajax possible!
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");
					return false;
				}
			}
		}
		// Create a function that will receive data sent from the server
		ajaxRequest.onreadystatechange = function(){
			if(ajaxRequest.readyState == 4){
				  querycount = parseInt(document.getElementById("querytable").getAttribute("totalqueries")) + 1;
				  
				  renderQueryBox('/getqueries/' + username + '/' + querycount,'queriesdiv', 1);
				  var link = document.getElementById('query' + querycount);
				  if(link != undefined) {
					link.click();
				  } else {
				  	var link2 = document.getElementById('query1');
				  	if(link2 != undefined) {
						link2.click();
				  	}
				  	
				  }
		
				  
				  $('#keyword').val('');
				  $('#dollar_limit').val('');
				
			}
		}
		ajaxRequest.open("GET", url, true);
		ajaxRequest.send(null); 
		
	
		
	}
	
	function removeQuery(url,highlightIndex, queryid, price_max, price_min, price_high, price_low, daysfilter, username)
	{
		var ajaxRequest;  // The variable that makes Ajax possible!
		
		try{
			// Opera 8.0+, Firefox, Safari
			ajaxRequest = new XMLHttpRequest();
		} catch (e){
			// Internet Explorer Browsers
			try{
				ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
			} catch (e) {
				try{
					ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
				} catch (e){
					// Something went wrong
					alert("Your browser broke!");
					return false;
				}
			}
		}
		
		
		ajaxRequest.open("GET", url, false); // false: synchronous call to eliminate weird UI behavior
		ajaxRequest.send(null); 
		
		// Re render query box and deal results after deleting a query. Immediately see results of action
		renderQueryBox('/getqueries/' + username + '/' + highlightIndex,'queriesdiv', 1);
       	var link = document.getElementById('query1');
       	if(link != undefined) {
	  		link.click();
	  		
	  	}
	  	else{
	  		var div = "";
	  		var ajaxDisplay;
	  		var divs = ['dealresultsdiv', 'filtersdiv', 'savedknopons', 'mapresultsdiv', 'localmaps'];
	  		for (div in divs) {
	  		 	ajaxDisplay = document.getElementById(divs[div]);
	  		 	if(ajaxDisplay != null) {
					ajaxDisplay.innerHTML = "";
				}
			}
	  	}
       
		
	}
   
    
	
	
