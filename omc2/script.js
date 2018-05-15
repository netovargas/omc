$(document).ready(function(){
    var jsondata;
    $.getJSON("articledata.json", function(data) {
      console.log("success");
      jsondata = data;
      
      var articleContainer = $(".grid-container");
      for (var i in jsondata) {
        // create article div
        var articleDiv = $("<div></div>");
        articleDiv.attr("class", "grid-item");
        // create div content
        var headlineText = jsondata[i]["title"];
        var createdDate = new Date(jsondata[i]["createdTime"]);
        var today = new Date();
        if ((today - createdDate) < 604800000) {
          console.log(today - createdDate);
          headlineText = "*" + headlineText;
        }
        var headline = $("<a></a>").text(headlineText).attr("href", jsondata[i]["url"]);
        headline.attr("class", "articleTitle");
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