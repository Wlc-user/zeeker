const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat, BorderStyle, WidthType,
        ShadingType, HeadingLevel, PageNumber } = require('docx');
const fs = require('fs');

// 样式配置
const COLORS = {
    primary: "1F4E79",      // 深蓝
    secondary: "2E75B6",    // 中蓝
    accent: "5B9BD5",       // 浅蓝
    dark: "333333",         // 深灰
    gray: "666666",         // 中灰
    lightGray: "F2F2F2",    // 浅灰背景
    white: "FFFFFF"
};

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// 创建水平分隔线
function createDivider(color = COLORS.accent) {
    return new Paragraph({
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: color, space: 1 } },
        spacing: { before: 100, after: 100 }
    });
}

// 创建标题
function createSectionTitle(text) {
    return new Paragraph({
        children: [
            new TextRun({
                text: text,
                bold: true,
                size: 28,
                color: COLORS.primary,
                font: "微软雅黑"
            })
        ],
        spacing: { before: 300, after: 150 }
    });
}

// 创建要点段落
function createBullet(text, bold = false) {
    return new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: [
            new TextRun({
                text: text,
                size: 22,
                color: COLORS.dark,
                bold: bold,
                font: "微软雅黑"
            })
        ],
        spacing: { before: 60, after: 60 }
    });
}

// 创建子项
function createSubItem(text) {
    return new Paragraph({
        numbering: { reference: "sub-bullets", level: 0 },
        children: [
            new TextRun({
                text: text,
                size: 20,
                color: COLORS.gray,
                font: "微软雅黑"
            })
        ],
        spacing: { before: 40, after: 40 }
    });
}

// 创建普通段落
function createParagraph(text, options = {}) {
    return new Paragraph({
        children: [
            new TextRun({
                text: text,
                size: options.size || 22,
                color: options.color || COLORS.dark,
                bold: options.bold || false,
                font: "微软雅黑"
            })
        ],
        spacing: { before: options.before || 60, after: options.after || 60 },
        alignment: options.alignment || AlignmentType.LEFT
    });
}

// 创建两列信息行
function createInfoRow(label, value) {
    return new TableRow({
        children: [
            new TableCell({
                borders: noBorders,
                width: { size: 1800, type: WidthType.DXA },
                children: [new Paragraph({
                    children: [new TextRun({ text: label, bold: true, size: 22, color: COLORS.primary, font: "微软雅黑" })]
                })]
            }),
            new TableCell({
                borders: noBorders,
                width: { size: 7560, type: WidthType.DXA },
                children: [new Paragraph({
                    children: [new TextRun({ text: value, size: 22, color: COLORS.dark, font: "微软雅黑" })]
                })]
            })
        ]
    });
}

// 创建技能标签行
function createSkillRow(title, skills) {
    return new TableRow({
        children: [
            new TableCell({
                borders: noBorders,
                width: { size: 2000, type: WidthType.DXA },
                children: [new Paragraph({
                    children: [new TextRun({ text: title, bold: true, size: 22, color: COLORS.primary, font: "微软雅黑" })]
                })]
            }),
            new TableCell({
                borders: noBorders,
                width: { size: 7360, type: WidthType.DXA },
                children: [new Paragraph({
                    children: skills.map(skill => new TextRun({ text: skill, size: 22, color: COLORS.dark, font: "微软雅黑" }))
                })]
            })
        ]
    });
}

// 项目经验表格
function createProjectTable(projects) {
    const rows = projects.map(p => new TableRow({
        children: [
            new TableCell({
                borders: noBorders,
                width: { size: 9360, type: WidthType.DXA },
                children: [
                    new Paragraph({
                        children: [new TextRun({ text: p.title, bold: true, size: 24, color: COLORS.secondary, font: "微软雅黑" })],
                        spacing: { before: 150, after: 80 }
                    }),
                    new Paragraph({
                        children: [
                            new TextRun({ text: p.period, size: 20, color: COLORS.gray, font: "微软雅黑" }),
                            new TextRun({ text: " | ", size: 20, color: COLORS.gray, font: "微软雅黑" }),
                            new TextRun({ text: p.tech, size: 20, color: COLORS.gray, font: "微软雅黑" })
                        ],
                        spacing: { after: 100 }
                    }),
                    ...p.items.map(item => createBullet(item))
                ]
            })
        ]
    }));
    
    return new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [9360],
        rows: rows
    });
}

// 创建简历文档
const doc = new Document({
    numbering: {
        config: [
            {
                reference: "bullets",
                levels: [{
                    level: 0,
                    format: LevelFormat.BULLET,
                    text: "\u2022",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 400, hanging: 200 } } }
                }]
            },
            {
                reference: "sub-bullets",
                levels: [{
                    level: 0,
                    format: LevelFormat.BULLET,
                    text: "-",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 700, hanging: 200 } } }
                }]
            }
        ]
    },
    styles: {
        default: {
            document: {
                run: { font: "微软雅黑", size: 22, color: COLORS.dark }
            }
        }
    },
    sections: [{
        properties: {
            page: {
                size: { width: 12240, height: 15840 },
                margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
            }
        },
        headers: {
            default: new Header({
                children: [
                    new Paragraph({
                        border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COLORS.accent, space: 1 } },
                        children: [new TextRun({ text: "求职简历", size: 20, color: COLORS.gray, font: "微软雅黑" })],
                        alignment: AlignmentType.RIGHT
                    })
                ]
            })
        },
        footers: {
            default: new Footer({
                children: [
                    new Paragraph({
                        border: { top: { style: BorderStyle.SINGLE, size: 6, color: COLORS.lightGray, space: 1 } },
                        children: [
                            new TextRun({ text: "软件测试工程师 | ", size: 18, color: COLORS.gray, font: "微软雅黑" }),
                            new TextRun({ text: "联系电话: ", size: 18, color: COLORS.gray, font: "微软雅黑" }),
                            new TextRun({ text: " | ", size: 18, color: COLORS.gray, font: "微软雅黑" }),
                            new TextRun({ text: "Page ", size: 18, color: COLORS.gray, font: "微软雅黑" }),
                            new TextRun({ children: [PageNumber.CURRENT], size: 18, color: COLORS.gray, font: "微软雅黑" })
                        ],
                        alignment: AlignmentType.CENTER
                    })
                ]
            })
        },
        children: [
            // ========== 个人信息部分 ==========
            new Paragraph({
                children: [
                    new TextRun({ text: "张三", bold: true, size: 52, color: COLORS.primary, font: "微软雅黑" })
                ],
                alignment: AlignmentType.CENTER,
                spacing: { before: 200, after: 100 }
            }),
            new Paragraph({
                children: [
                    new TextRun({ text: "软件测试工程师", size: 28, color: COLORS.secondary, font: "微软雅黑" })
                ],
                alignment: AlignmentType.CENTER,
                spacing: { after: 200 }
            }),
            
            // 联系方式
            new Table({
                width: { size: 9360, type: WidthType.DXA },
                columnWidths: [4680, 4680],
                borders: { insideH: noBorder, insideV: noBorder, ...noBorders },
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({
                                borders: noBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [new Paragraph({
                                    alignment: AlignmentType.CENTER,
                                    children: [new TextRun({ text: "电话: 138-xxxx-xxxx", size: 20, color: COLORS.gray, font: "微软雅黑" })]
                                })]
                            }),
                            new TableCell({
                                borders: noBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [new Paragraph({
                                    alignment: AlignmentType.CENTER,
                                    children: [new TextRun({ text: "邮箱: example@email.com", size: 20, color: COLORS.gray, font: "微软雅黑" })]
                                })]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({
                                borders: noBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [new Paragraph({
                                    alignment: AlignmentType.CENTER,
                                    children: [new TextRun({ text: "GitHub: github.com/username", size: 20, color: COLORS.gray, font: "微软雅黑" })]
                                })]
                            }),
                            new TableCell({
                                borders: noBorders,
                                width: { size: 4680, type: WidthType.DXA },
                                children: [new Paragraph({
                                    alignment: AlignmentType.CENTER,
                                    children: [new TextRun({ text: "城市: 上海市", size: 20, color: COLORS.gray, font: "微软雅黑" })]
                                })]
                            })
                        ]
                    })
                ]
            }),
            
            createDivider(),
            
            // ========== 专业技能 ==========
            createSectionTitle("专业技能"),
            
            new Table({
                width: { size: 9360, type: WidthType.DXA },
                columnWidths: [9360],
                borders: { insideH: noBorder, insideV: noBorder, ...noBorders },
                rows: [
                    createSkillRow("测试技能", ["功能测试", "自动化测试", "接口测试", "性能测试", "移动端测试"]),
                    createSkillRow("编程语言", ["Python", "Java", "SQL", "JavaScript"]),
                    createSkillRow("测试工具", ["Selenium", "Appium", "Postman", "JMeter", "Fiddler"]),
                    createSkillRow("框架", ["pytest", "unittest", "Selenium Grid"]),
                    createSkillRow("其他", ["Git", "Docker", "Jenkins", "Linux", "MySQL"])
                ]
            }),
            
            createDivider(),
            
            // ========== 项目经验 ==========
            createSectionTitle("项目经验"),
            
            // 项目一：极氪销售助手
            new Paragraph({
                children: [
                    new TextRun({ text: "ZEEKR极氪智能销售助手系统", bold: true, size: 26, color: COLORS.secondary, font: "微软雅黑" })
                ],
                spacing: { before: 200, after: 80 }
            }),
            new Paragraph({
                children: [
                    new TextRun({ text: "项目周期: ", size: 20, color: COLORS.gray, font: "微软雅黑" }),
                    new TextRun({ text: "2024.03 - 2024.04", size: 20, color: COLORS.gray, font: "微软雅黑" }),
                    new TextRun({ text: "    角色: ", size: 20, color: COLORS.gray, font: "微软雅黑" }),
                    new TextRun({ text: "测试工程师（独立负责全链路测试）", size: 20, color: COLORS.gray, font: "微软雅黑" })
                ],
                spacing: { after: 100 }
            }),
            new Paragraph({
                children: [
                    new TextRun({ text: "项目描述: ", bold: true, size: 22, color: COLORS.dark, font: "微软雅黑" }),
                    new TextRun({ text: "基于知识图谱的极氪车型销售推荐系统，支持多维度图片检索与智能对话", size: 22, color: COLORS.dark, font: "微软雅黑" })
                ],
                spacing: { after: 80 }
            }),
            
            createBullet("需求分析与测试用例设计", true),
            createSubItem("分析产品需求文档，提取功能点，设计功能测试用例 50+"),
            createSubItem("覆盖车型推荐、图片检索、对话交互等核心模块"),
            createSubItem("使用思维导图梳理业务流程，确保覆盖完整"),
            
            createBullet("功能测试执行", true),
            createSubItem("测试车型推荐逻辑：输入\"家用\"、\"科技\"、\"商务\"等需求，验证推荐结果准确性"),
            createSubItem("测试意图识别：验证12种用户意图的准确识别"),
            createSubItem("测试图片关联：根据用户咨询车型自动展示对应图片"),
            createSubItem("使用 Excel 管理缺陷，全流程跟踪 8+ 个缺陷"),
            
            createBullet("数据采集与验证", true),
            createSubItem("编写爬虫脚本从汽车之家抓取车型数据，验证数据准确性"),
            createSubItem("清洗和标注图片 300+ 张，建立图片分类体系"),
            
            createBullet("界面与兼容性测试", true),
            createSubItem("测试 Streamlit 界面在不同分辨率下的显示效果"),
            createSubItem("验证多浏览器（Chrome、Firefox、Edge）兼容性"),
            
            new Paragraph({
                children: [
                    new TextRun({ text: "测试成果: ", bold: true, size: 22, color: COLORS.dark, font: "微软雅黑" }),
                    new TextRun({ text: "累计发现并跟踪缺陷 12 个，上线后无严重遗漏；测试用例覆盖率达到 95%", size: 22, color: COLORS.dark, font: "微软雅黑" })
                ],
                spacing: { before: 100, after: 100 }
            }),
            
            // 项目二：电商平台测试
            new Paragraph({
                children: [
                    new TextRun({ text: "XX电商平台测试项目（实训）", bold: true, size: 26, color: COLORS.secondary, font: "微软雅黑" })
                ],
                spacing: { before: 300, after: 80 }
            }),
            new Paragraph({
                children: [
                    new TextRun({ text: "项目周期: ", size: 20, color: COLORS.gray, font: "微软雅黑" }),
                    new TextRun({ text: "2023.XX - 2023.XX", size: 20, color: COLORS.gray, font: "微软雅黑" }),
                    new TextRun({ text: "    技术栈: ", size: 20, color: COLORS.gray, font: "微软雅黑" }),
                    new TextRun({ text: "Selenium + Appium + JMeter + Postman", size: 20, color: COLORS.gray, font: "微软雅黑" })
                ],
                spacing: { after: 100 }
            }),
            
            createBullet("Web端自动化测试", true),
            createSubItem("使用 Selenium + Python 编写自动化测试脚本，覆盖用户登录、商品搜索、下单支付等核心流程"),
            createSubItem("自动化用例 30+，脚本可复用性强"),
            
            createBullet("App端兼容性测试", true),
            createSubItem("使用 Appium 进行 Android/iOS 应用测试，覆盖主流机型 10+ 台"),
            
            createBullet("接口测试", true),
            createSubItem("使用 Postman 进行 API 接口测试，设计接口测试用例 50+"),
            createSubItem("使用 Newman 实现接口测试自动化"),
            
            createBullet("性能测试", true),
            createSubItem("使用 JMeter 进行压力测试，测试 100/500/1000 并发用户场景"),
            createSubItem("分析吞吐量、响应时间、TPS 等关键性能指标"),
            
            createDivider(),
            
            // ========== 工作流程 ==========
            createSectionTitle("测试流程与工具"),
            
            new Table({
                width: { size: 9360, type: WidthType.DXA },
                columnWidths: [4680, 4680],
                borders: { insideH: border, insideV: border, ...noBorders },
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({
                                borders: borders,
                                width: { size: 4680, type: WidthType.DXA },
                                shading: { fill: COLORS.lightGray, type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "测试类型", bold: true, size: 22, color: COLORS.primary, font: "微软雅黑" })], alignment: AlignmentType.CENTER })]
                            }),
                            new TableCell({
                                borders: borders,
                                width: { size: 4680, type: WidthType.DXA },
                                shading: { fill: COLORS.lightGray, type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "熟练工具", bold: true, size: 22, color: COLORS.primary, font: "微软雅黑" })], alignment: AlignmentType.CENTER })]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "功能测试", size: 20, font: "微软雅黑" })] })] }),
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "手动测试、边界值分析", size: 20, font: "微软雅黑" })] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "自动化测试", size: 20, font: "微软雅黑" })] })] }),
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Selenium、pytest", size: 20, font: "微软雅黑" })] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "接口测试", size: 20, font: "微软雅黑" })] })] }),
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Postman、JMeter", size: 20, font: "微软雅黑" })] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "缺陷管理", size: 20, font: "微软雅黑" })] })] }),
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "JIRA、禅道、Excel", size: 20, font: "微软雅黑" })] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "抓包分析", size: 20, font: "微软雅黑" })] })] }),
                            new TableCell({ borders: borders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Fiddler、Charles", size: 20, font: "微软雅黑" })] })] })
                        ]
                    })
                ]
            }),
            
            createDivider(),
            
            // ========== 自我评价 ==========
            createSectionTitle("自我评价"),
            
            createBullet("细心耐心：善于发现细节问题，测试用例设计考虑全面", false),
            createBullet("逻辑思维：能够梳理复杂业务流程，快速定位问题根源", false),
            createBullet("学习能力：对新工具、新技术保持好奇，主动学习并应用到工作中", false),
            createBullet("沟通能力：能够与开发、产品有效沟通，推动问题解决", false),
            createBullet("团队协作：积极参与团队讨论，配合完成项目目标", false),
            
            new Paragraph({ children: [], spacing: { before: 300 } }),
            new Paragraph({
                children: [
                    new TextRun({ text: "感谢您阅读我的简历，期待与您进一步沟通！", size: 22, color: COLORS.gray, font: "微软雅黑", italics: true })
                ],
                alignment: AlignmentType.CENTER
            })
        ]
    }]
});

// 生成文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("e:/pyspace/zeeker/软件测试简历_专业版.docx", buffer);
    console.log("简历已生成: e:/pyspace/zeeker/软件测试简历_专业版.docx");
});
