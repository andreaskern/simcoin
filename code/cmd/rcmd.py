import config


def preprocess(path):
    return ';'.join(
        [ f'cp reporter/{config.preprocess_r_file_name} {path}'
        , f'cd {path}'
        , f'Rscript {config.preprocess_r_file_name}'
        ]
    )


def create_report(path):
    return ';'.join(
        [ f'cp reporter/{config.report_rmd_file_name} {path}'
        , f'cd {path}'
        , f'mv SetpTimes_new.csv step_times.csv'
        , r'R -e library\(rmarkdown\)\;'
          r'rmarkdown::render\(\"' + f"{config.report_rmd_file_name}" + r'\",\"pdf_document\"\)\;'
          r'q\(\)'
        ]
    )
