function getWindow(lastDate) {
    var window = $('meta[name=x_window]').attr("content");
    var lastDateObj = new Date(lastDate);
    var windowDateObj = lastDateObj.setSeconds(lastDateObj.getSeconds() - window);
    return windowDateObj;
}

function makePlotly(x, y1, y2){
    var plotDiv = document.getElementById("plot");
    var traces1 = [{
        x: x,
        y: y1,
        mode: 'lines',
        name: 'Actual Level',
        line: {
            dash: 'solid',
            width: 3
        }
    }];
    var traces2 = [{
        x: x,
        y: y2,
        mode: 'lines',
        name: 'Reference',
        marker: {
            color: 'rgb(189,189,189)',
            line: {
                dash: 'dashdot',
                color: 'rgb(189,189,189)',
                width: 3
            }
        }

    }];
    var windowDateObj = getWindow(x[x.length - 1])
    console.log(windowDateObj)
    var layout = {
        font: {size: 18},
        margin: { t: 0 },
        xaxis: {
            range: [windowDateObj,  x[x.length - 1]],
            rangeslider: {range: [x[0], x[x.length - 1]]},
            type: 'date'
        },
        yaxis: {
            range: [0, 110]
        }
    };

    var additional_params = {
        responsive: true
    };

    Plotly.plot(plotDiv, traces1, layout, additional_params);
    Plotly.plot(plotDiv, traces2, layout, additional_params);
};

function addZero(i) {
  if (i < 10) {
    i = "0" + i;
  }
  return i;
}

function streamPlotly(x, y1, y2, plot_start){
    var plotDiv = document.getElementById("plot");
    var data_update_0 = {x: [x], y: [y1]};
    var data_update_1 = {x: [x], y: [y2]};
    var windowDateObj = getWindow(x);
    var layout_update = {xaxis: {
        range: [windowDateObj, x[x.length - 1]],
        rangeslider: {range: [plot_start, x[x.length - 1]]}
    }};
    console.log("x: " + x);
    console.log("y: " + y1);
    Plotly.update(plotDiv, {}, layout_update);
    Plotly.extendTraces(plotDiv, data_update_0, [0]);
    Plotly.extendTraces(plotDiv, data_update_1, [1]);
};

$(function() {

    var today = new Date();
    var mo = addZero((today.getMonth()+1));
    var d = addZero(today.getDate());
    var h = addZero(today.getHours());
    var m = addZero(today.getMinutes());
    var s = addZero(today.getSeconds());
    var date = today.getFullYear() + '-' + mo + '-' + d;
    var time = h + ":" + m + ":" + s;
    var dateTime = date + ' ' + time;

    var x = [dateTime];
    var y1 = [0];
    var y2 = [50];

    makePlotly(x, y1, y2);
})

//
// var url = 'http://' + document.domain + ':' + 5000
// var socket = io.connect(url);
//
// socket.on('connect', function(msg) {
//     console.log('connected to websocket on ' + url);
// });
//
// socket.on('bootstrap', function (msg) {
//     console.log("boot")
//     plot_start = msg.x[0];
//     makePlotly( msg.x, msg.y )
// });
//
// socket.on('update', function (msg) {
//     streamPlotly( msg.x, msg.y )
// });
