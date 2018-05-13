var linePlot, spiderPlot, weights, video, audio, text;

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
         //   console.log(point)
            var series = linePlot.series[0],
            shift = series.data.length > 200; // shift if the series is longer than 20
            
            /*
            // format:
            //[a, d, h, n, sad, sur, frame]    
            //line plot
            linePlot.series[0].addPoint([point[6], point[0]], true);
            linePlot.series[1].addPoint([point[6], point[1]], true);
            linePlot.series[2].addPoint([point[6], point[2]], true);
            linePlot.series[3].addPoint([point[6], point[3]], true);
            linePlot.series[4].addPoint([point[6], point[4]], true);
            linePlot.series[5].addPoint([point[6], point[5]], true);
            
            //spider plot
            spiderPlot.series[0].setData([point[0], point[1], point[2], point[3], point[4], point[5]],true)
     
            //weights plot
            weights.series[0].setData([point[6], point[6], point[6]], true)

            //video plot

            //audio plot

            //text plot
            */


            //format : [weightedAvgProbs, weights, videoProbs, toneProbs, speechProbs, videoAttr]
            // size :  [    6                3           6       6           6              2]
             //line plot
             linePlot.series[0].addPoint([point[27], point[0]], true);
             linePlot.series[1].addPoint([point[27], point[1]], true);
             linePlot.series[2].addPoint([point[27], point[2]], true);
             linePlot.series[3].addPoint([point[27], point[3]], true);
             linePlot.series[4].addPoint([point[27], point[4]], true);
             linePlot.series[5].addPoint([point[27], point[5]], true);
            
            //spider plot
            spiderPlot.series[0].setData([point[0], point[1], point[2], point[3], point[4], point[5]],true)
    
            //weights plot
            weights.series[0].setData([point[6], point[7], point[8]], true)

            //video plot
            video.series[0].setData([point[9], point[10], point[11], point[12], point[13], point[14]], true)
            //audio plot
            audio.series[0].setData([point[15], point[16], point[17], point[18], point[19], point[20]], true)
            //text plot
            text.series[0].setData([point[21], point[22], point[23], point[24], point[25], point[26]], true)
            
            // call it again after one second
            setTimeout(requestData, 1000);
        },
        cache: false
    });
}

function refreshImage() {
    document.picture.src="/static/video.png?a=" +String(Math.random()*999);
    setTimeout('refreshImage()', 100)
}

$(document).ready(function() {
    refreshImage()
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
                return 'Frame: ' + this.key + ' Probability: ' + this.y;
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
                text: 'Frame',
            }
        },
        yAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            title: {
                text: 'Probability',
            }
        },
           // format:
            //[a, d, h, n, sad, sur, frame]
        series: [ { name: 'Anger',data: [] },{ name: 'Disgust',data: [] },
                  { name: 'Happy',data: [] },{ name: 'Neutral',data: [] },
                  { name: 'Sad',data: []   },{ name: 'Surprise', data: [] }, ]
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
    
    weights = new Highcharts.Chart({
        chart: {
            type: 'bar',
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
                    enabled: true
                }
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -40,
            y: 80,
            floating: true,
            borderWidth: 1,
            backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
            shadow: true
        },
        credits: {
            enabled: false
        },
        series: [{
            name: 'Influence',
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
        subtitle: {
            text: '<a href="https://en.wikipedia.org/wiki/World_population">More info</a>'
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
        subtitle: {
            text: ' <a href="https://en.wikipedia.org/wiki/World_population">More info</a>'
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
        subtitle: {
            text: '<a href="https://en.wikipedia.org/wiki/World_population">More info</a>'
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