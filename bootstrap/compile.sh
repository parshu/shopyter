make
echo "Customizing bootstrap-responsive.css ..."
sed '548 s/.*/    margin-left: 8px;/' docs/assets/css/bootstrap-responsive.css > test1
sed '216 s/.*/    margin-left: 8px;/' test1 > test2
sed '312 s/.*/    margin-left: 8px;/' test2 > test3
sed '452 s/.*/    margin-left: 8px;/' test3 > docs/assets/css/bootstrap-responsive.css
echo "Done customizing bootstrap-responsive.css ..."
echo "Customizing bootstrap.css ..."
sed '194 s/.*/   margin-left: 8px;/' docs/assets/css/bootstrap.css > test1
sed '319 s/.*/   margin-left: 8px;/' test1 > test2
sed '3208 s/.*/   margin-bottom: 0px;/' test2 > test21
sed '409 s/.*/   padding-left: 70px;/' test21 > test3
sed '2594 s/.*/   background-color: #AAAAAA;/' test3 > test31
sed '2595 s/.*/   *background-color: #AAAAAA;/' test31 > test32
sed '2596 s/.*//' test32 > test33
sed '2597 s/.*//' test33 > test34
sed '2598 s/.*//' test34 > test35
sed '2599 s/.*//' test35 > test36
sed '2600 s/.*//' test36 > test37
sed '2601 s/.*//' test37 > test38
sed '2493 s/.*/   padding: 0px;/' test38 > test4
sed '2496 s/.*/   border: 0px solid #eee;/' test4 > test5
sed '2497 s/.*/   border: 0px solid rgba(0, 0, 0, 0.05);/' test5 > test6
sed '4478 s/.*/   margin-bottom: 2px;/' test6 > docs/assets/css/bootstrap.css
echo "Done customizing bootstrap.css ..."
echo "Removing temp files..."
rm test*
echo "Done."





