var linePlot, spiderPlot, weights, video, audio, text;
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
             linePlot.series[0].addPoint([time, point[0]], true);      
             linePlot.series[1].addPoint([time, point[1]], true);
             linePlot.series[2].addPoint([time, point[2]], true);
             linePlot.series[3].addPoint([time, point[3]], true);
        
            
            //spider plot
            spiderPlot.series[0].setData([point[0], point[1], point[2], point[3]],true);
    
            //weights plot
            weights.series[0].setData([point[4], point[5], point[6]], true);

            //video plot
            video.series[0].setData([point[7], point[8], point[9], point[10], point[11], point[12]], true);

            //audio plot
            audio.series[0].setData([point[13], point[14], point[15], point[16]], true);

            //text plot
            text.series[0].setData([point[17], point[18], point[19], point[20]], true);
            
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
    // 0 to 3:
    var result = "";
    var highest = Math.max(point[0], point[1], point[2], point[3]);
    switch(highest) {
        case point[0]:
            return "Neutral";
            break;
        case point[1]:
            return "Sadness/Fear";
            break;
        case point[2]:
            return "Anger/Frustration/Disgust";
            break;
        case point[3]:
            return "Happiness/Excitment/Surprise";
            break;
        default:
            return "Error!";     
    }
}

function refreshImage() {
    document.picture.src="/static/video.png?a=" +String(Math.random()*999);
    setTimeout('refreshImage()', 100);
}

$(document).ready(function() {
    refreshImage();
    linePlot = new Highcharts.Chart({
        chart: {
            renderTo: 'combinedLine',
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
            renderTo: 'combinedSpider',
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
    
    weights = new Highcharts.Chart({
        chart: {
            type: 'column',
            renderTo: 'weights',
        },
        title: {
            text: 'Weights of individual modules'
        },
        xAxis: {
            range : 1,
            categories: ['Video', 'Audio', 'Text'],
            title: {
                text: null
            }
        },
        yAxis: {
            min: 0,
            max : 1,
            title: {
                text: 'Value',
                align: 'high'
            },
            labels: {
                overflow: 'justify'
            }
        },
        plotOptions: {
            bar: {
                dataLabels: {
                    enabled: true,
                    colorByPoint : true
                }
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
           
            floating: true,
            borderWidth: 1,
            backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
            shadow: true
        },
        credits: {
            enabled: false
        },
        series: [{
            name: 'Emphasis',
            data: []
        }]
    });

    video = new Highcharts.Chart({

        chart: {
            renderTo: 'video',
            polar: true,
            type: 'area'
        },
    
        title: {
            text: 'Video module',
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

    audio = new Highcharts.Chart({

        chart: {
            renderTo: 'audio',
            polar: true,
            type: 'area'
        },
    
        title: {
            text: 'Audio module',
            x: -80
        },
        pane: {
            size: '80%'
        },
    
        xAxis: {
            // format:
            //[a, d, h, n, sad, sur, frame]
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
            name: 'Probability of emotion',
            data: [],
            pointPlacement: 'on'
        }]
    
    });

    text = new Highcharts.Chart({

        chart: {
            renderTo: 'text',
            polar: true,
            type: 'area'
        },
    
        title: {
            text: 'Text module',
            x: -80
        },
        pane: {
            size: '80%'
        },
    
        xAxis: {
            // format:
            //[a, d, h, n, sad, sur, frame]
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
            name: 'Probability of emotion',
            data: [],
            pointPlacement: 'on'
        }]
    
    });



});