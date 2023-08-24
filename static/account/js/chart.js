$(function() {
  /* ChartJS
   * -------
   * Data and config for chartjs
   */
  'use strict';
  var data = {
    labels: ["Income", "Expence", "Loss/Porfit"],
    datasets: [{
      // label: '# of Votes',
      data: [100000, 75000, 25000],
      backgroundColor: [
        'rgba(73, 204, 26, 0.721)',
        'rgba(234, 26, 26, 0.721)',
        'rgba(19, 111, 192, 0.721)',
        
      ],
      borderColor: [
        
      ],
      borderWidth: 1,
      fill: false
    }]
  };
 
  var options = {
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    },
    legend: {
      display: false
    },
    elements: {
      point: {
        radius: 0
      }
    }

  };


  // Get context with jQuery - using jQuery's .get() method.
  if ($("#barChart").length) {
    var barChartCanvas = $("#barChart").get(0).getContext("2d");
    // This will get the first returned node in the jQuery collection.
    var barChart = new Chart(barChartCanvas, {
      type: 'bar',
      data: data,
      options: options
    });
  }
    
});