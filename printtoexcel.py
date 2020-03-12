
# ['inlettemp', 'catalystweight', 'residencetime', 'reactorP'] = DV
def printtoexcel(DV):
    # Printing to excel
    write_excel = create_excel_file('./results/pso_ga_results.xlsx')
    wb = openpyxl.load_workbook(write_excel)
    ws = wb[wb.sheetnames[-1]]

    ws.cell(1, 1).value = 'Optimal Decision Values'
    print_array_to_excel(DV, (2, 1), ws=ws, axis=1)
    print_array_to_excel(best, (3, 1), ws=ws, axis=1)

    genfit = logbook.select("gen")
    avgfit = logbook.select("avg")
    stdfit = logbook.select("std")
    minfit = logbook.select("min")
    maxfit = logbook.select("max")

    ws.cell(5, 1).value = 'gen'
    ws.cell(6, 1).value = 'avg'
    ws.cell(7, 1).value = 'std'
    ws.cell(8, 1).value = 'min'
    ws.cell(9, 1).value = 'max'

    print_array_to_excel(genfit, (5, 2), ws=ws, axis=1)
    print_array_to_excel(avgfit, (6, 2), ws=ws, axis=1)
    print_array_to_excel(stdfit, (7, 2), ws=ws, axis=1)
    print_array_to_excel(minfit, (8, 2), ws=ws, axis=1)
    print_array_to_excel(maxfit, (9, 2), ws=ws, axis=1)

    wb.save(write_excel)
    return

