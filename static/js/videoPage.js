var linePlot, spiderPlot;
var time = 0;
/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
// If changes are not being reflected in the webpage, press Ctrl+Shift+R(Linux)
// to fully reload the webpage without any caching.
function requestData() {
    $.ajax({
        url: '/live-data',
        success: function(point) {
          //  console.log(point)
            var series = linePlot.series[0];
            shift = series.data.length > 200; // shift if the series is longer than 20
            
            
            //format : [weightedAvgProbs, weights, videoProbs, toneProbs, speechProbs, videoAttrs, toneAttrs,  combinedEmotion]
            // size :  [    4                3           6       4           4              2       2            1 ]
            linePlot.series[0].addPoint([time, point[7]], true);      
            linePlot.series[1].addPoint([time, point[8]], true);
            linePlot.series[2].addPoint([time, point[9]], true);
            linePlot.series[3].addPoint([time, point[10]], true);
            linePlot.series[4].addPoint([time, point[11]], true);
            linePlot.series[5].addPoint([time, point[12]], true);
            
            video.series[0].setData([point[7], point[8], point[9], point[10], point[11], point[12]], true);

            time +=1;
            
            var detEmotion = "Detected emotion: <strong>"+ getCombinedEmotion(point) +"</strong> <br><br><br><br><br>";
            $('#detectedEmotionBox').html(detEmotion);

            // call it again after one second
            setTimeout(requestData, 1000);
        },
        cache: false
    });
}

function getCombinedEmotion(point) {
      // 7 to 12:
      var result = "";
      var highest = Math.max(point[7], point[8], point[9], point[10],
                             point[11], point[12]);
      switch(highest) {
            case point[7]:
                return "Anger";
                break;
            case point[8]:
                return "Disgust";
                break;
            case point[9]:
                return "Happiness";
                break;
            case point[10]:
                return "Neutral";
                break;
            case point[11]:
                return "Sad";
                break;   
            case point[12]:
              return "Surprise";
              break; 
          default:
              return "Error!";     
      }
}

function refreshImage() {
    document.picture.src="/static/video.png?a=" +String(Math.random()*999);
    document.picture2.src="/static/video.png?a=" +String(Math.random()*999);
    setTimeout('refreshImage()', 100);
}

$(document).ready(function() {
    refreshImage();
    linePlot = new Highcharts.Chart({
        chart: {
            renderTo: 'videoLine',
            defaultSeriesType: 'spline',
            zoomType: 'xy',
            panning: true,
            events: {
                load: requestData
            }
        },
        tooltip:{
            formatter:function(){
                return 'Second: ' + this.key + ' Probability: ' + this.y;
            }
        },
        title: {
            text: 'Over time'
        },
        xAxis: {
          //  tickPixelInterval: 150,
          //  maxZoom: 20 * 1000
            minPadding: 0.2,
            maxPadding: 0.2,
            title: {
                text: 'Time elapsed(seconds)',
            }
        },
        yAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            min : 0,
            max : 100,
            title: {
                text: 'Probability',
            }
        },
           // format:
            //[a, d, h, n, sad, sur, frame]
        series: [ { name: 'Angry', data: [], color:'red'  },
                  { name: 'Disgusted', data: [], color:'brown' },
                  { name: 'Happy', data: [], color:'green' },
                  { name: 'Neutral', data: [], color:'yellow' },
                  { name: 'Sad', data: [], color:'black' },
                  { name: 'Surprise', data: [], color:'blue' }
                  ]
    });

    video = new Highcharts.Chart({
        chart: {
            renderTo: 'videoSpider',
            polar: true,
            type: 'area'
        },
    
        title: {
            text: 'Instantaneous',
            x: -80
        },
        pane: {
            size: '80%'
        },
    
        xAxis: {
            // format:
            //[a, d, h, n, sad, sur, frame]
            categories: ['Angry', 'Disgusted', 'Happy', 'Neutral',
                'Sad', 'Surprise'],
            tickmarkPlacement: 'on',
            lineWidth: 0
        },
    
        yAxis: {
            gridLineInterpolation: 'polygon',
            lineWidth: 0,
            min: 0,
            max : 100
        },
    
        tooltip: {
            shared: true,
            pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}</b><br/>',
            hideDelay : 10
        },
    
        legend: {
            align: 'bottom',
            verticalAlign: 'top',
            y: 70,
            layout: 'vertical'
        },
    
        series: [{
            name: 'Probability of emotion',
            data: [],
            pointPlacement: 'on'
        }]
    
    });
    
});