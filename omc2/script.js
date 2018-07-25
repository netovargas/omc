// Returns the date of the last Friday that happened
// and today's date if today is Friday.
function getLastFriday()
{
  var date = new Date();
  var day = date.getDay();
  var prevFriday;
  if(date.getDay() == 4){
    prevFriday = date;
  } else if (date.getDay() == 5 || date.getDay() == 6) {
    prevFriday = new Date().setDate(date.getDate() - (date.getDay() % 4));
  } else {
    prevFriday = new Date().setDate(date.getDate() - ((date.getDay() + 7) % 4));
  }
  return prevFriday;
}

function loadFilter(filterType)
{
  if (filterType == 'all') {
    $(".grid-item").css( "display", "inline" );
  } else {
    $(".grid-item").css( "display", "none" );
    $("."+filterType).css( "display", "inline");
  }
}

$(document).ready(function(){
    var jsondata;
    $.getJSON("articledata.json", function(data) {
      console.log("success");
      jsondata = data;
      
      var articleContainer = $(".grid-container");
      for (var i in jsondata) {
        // create article div
        var articleDiv = $("<div></div>");
        articleDiv.attr("class", "grid-item " + jsondata[i]["type"]);
        // create div content
        var headlineText = jsondata[i]["title"];
        var createdDate = new Date(jsondata[i]["createdTime"]);
        var lastFriday = getLastFriday();
        var headline = $("<a></a>").text(headlineText).attr("href", jsondata[i]["url"]);
        headline.attr("class", "articleTitle");
        if ((lastFriday - createdDate) < 604800000) {
          console.log(lastFriday - createdDate);
          headline.prepend("<sup>new</sup>");
        }
        var readTime;
        if (jsondata[i]["type"] == "read") {
          if (jsondata[i]["readTime"] == -1) {
            readTime = $("<p></p>").text("Article");
          } else {
            readTime = $("<p></p>").text(jsondata[i]["readTime"] + " minutes");
          }
        } else if (jsondata[i]["type"] == "shop") {
          readTime = $("<p></p>").text("Shopping Link");
        } else {
          typeString = jsondata[i]["type"];
          readTime = $("<p></p>").text(typeString.charAt(0).toUpperCase() + typeString.slice(1));
        }
        readTime.attr("class", "readingtime");
        // append all
        articleDiv.append(headline[0]);
        articleDiv.append(readTime[0]);
        articleContainer.append(articleDiv);
      }
    });
  });