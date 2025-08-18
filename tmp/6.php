<?
function buy($req)
{
    $req=json_decode($req);
    $money = $_SESSION['money'];
    $numbers = $req['numbers'];
    $win_numbers = random_win_nums();
    $same_count = 0;
    for ($i = 0; $i < 7; $i++) {
        if ($numbers[$i] == $win_numbers[$i]) {
            $same_count++;
        }
    }
    switch ($same_count) {
        case 2:
            $prize = 5;
            break;
        case 3:
            $prize = 20;
            break;
        case 4:
            $prize = 300;
            break;
        case 5:
            $prize = 1800;
            break;
        case 6:
            $prize = 200000;
            break;
        case 7:
            $prize = 5000000;
            break;
        default:
            $prize = 0;
            break;
    }
    $money += $prize - 2;
    $_SESSION['money'] = $money;
    response(['status' => 'ok', 'numbers' => $numbers, 'win_numbers' => $win_numbers, 'money' => $money, 'prize' => $prize]);
}