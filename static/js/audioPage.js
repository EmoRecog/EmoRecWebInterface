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
            //console.log(point);
            var series = linePlot.series[0];
            shift = series.data.length > 200; // shift if the series is longer than 20
            
            
            //format : [weightedAvgProbs, weights, videoProbs, toneProbs, speechProbs, videoAttrs, toneAttrs,  combinedEmotion]
            // size :  [    4                3           6       4           4              2       2            1 ]
             //line plot
             linePlot.series[0].addPoint([time, point[13]], true);      
             linePlot.series[1].addPoint([time, point[14]], true);
             linePlot.series[2].addPoint([time, point[15]], true);
             linePlot.series[3].addPoint([time, point[16]], true);
              
            //spider plot
            spiderPlot.series[0].setData([point[13], point[14], point[15], point[16]],true);
    
            //utterance plot 
            // var i;
            // for(i = 27; i < point.length; i++) {
            //     utterancePlot.series[0].addPoint([i - 27], point[i], true);
            // }

            time +=1;
            
            var detEmotion = "<h4 class=\"alert-heading\">Detected emotion:</h4> <strong>"+ getCombinedEmotion(point) +"</strong> <br><br><br><br><br>";
            $('#detectedEmotionBox').html(detEmotion);
            
            // call it again after one second
            setTimeout(requestData, 1000);
        },
        cache: false
    });
}

function getCombinedEmotion(point) {
    // 13 to 16:
    var result = "";
    var highest = Math.max(point[13], point[14], point[15], point[16]);
    switch(highest) {
        case point[13]:
            return "Neutral";
            break;
        case point[14]:
            return "Sadness/Fear";
            break;
        case point[15]:
            return "Anger/Frustration/Disgust";
            break;
        case point[16]:
            return "Happiness/Excitment/Surprise";
            break;
        default:
            return "Error!";     
    }
}

$(document).ready(function() {

    linePlot = new Highcharts.Chart({
        chart: {
            renderTo: 'audioLine',
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
        series: [ { name: 'Neutral',data: [], color:'yellow'  },
                  { name: 'Sadness/Fear',data: [], color:'black' },
                  { name: 'Anger/Frustration/Disgust',data: [], color:'red' },
                  { name: 'Happiness/Excitment/Surprise',data: [], color:'green'},
                  ]
    });

    spiderPlot = new Highcharts.Chart({

        chart: {
            renderTo: 'audioSpider',
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
            
            categories: ['Neutral', 'Sadness/<br/>Fear', 'Anger/<br/>Frustration/<br/>Disgust', 'Happiness/<br/>Excitment/<br/>Surprise'],
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
            name: 'Probabilities',
            data: [],
            pointPlacement: 'on'
        }]
    
    });
    
});