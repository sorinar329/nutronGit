// Lists of Inputs
dailyUsage = [
    ['label1', 'quantitiy1', 'function1'],
    ['label2', 'quantitiy2', 'function2'],
    ['label3', 'quantitiy3', 'function3'],
    ['label4', 'quantitiy4', 'function4'],
    ['label5', 'quantitiy5', 'function5'],
    ['label6', 'quantitiy6', 'function6'],
]

function saveInputOfDailyUsage(){
    var listofUsage = [];
    for (let i = 0; i <= dailyUsage.length; i++){
        var label = document.getElementById(dailyUsage[i][0]).valueOf();
        var num = document.getElementById(dailyUsage[i][1]).valueOf();
        var func = document.getElementById(dailyUsage[i][2]).valueOf();
        listofUsage.push({
            'type':label,
            'Num':num,
            'Func':func
        })
    }
    alert(listofUsage);
    return listofUsage;
}