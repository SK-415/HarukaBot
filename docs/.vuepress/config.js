module.exports = {
    title: 'HarukaBot',
    description: 'B站 消息推送 QQ机器人',
    head: [
      ['link', { rel: 'icon', href: '/logo.png' }]
    ],
    markdown: {
      lineNumbers: true
    },
    themeConfig: {
      logo: '/logo.png',
      repo: 'SK-415/HarukaBot',
      docsDir: 'docs',
      docsBranch: 'dev',
      editLinks: true,
      editLinkText: '在 GitHub 上编辑此页',
      lastUpdated: '上次更新',
      smoothScroll: true,

      nav: [
        { text: '主页', link: '/' },
        { text: '安装', link: '/install/' },
        { text: '使用帮助', link: '/usage/' },
        { text: '常见问题', link: '/usage/faq/' },
        { 
          text: '关于', 
          items: [
            { text: '更新日志', link: '/about/CHANGELOG/'},
            { text: '关于项目', link: '/about/' },
          ]
        }
      ],
      sidebar: {
        '/install/': [
          {
            title: '安装',
            collapsable: false,
            sidebar: 'auto',
            children: [
              '',
              'install-go-cqhttp',
              'install-HarukaBot',
              'congrats'
            ]
          }
        ],
        '/usage/': [
          {
            title: '使用帮助',
            collapsable: false,
            // sidebar: 'auto',
            children: [
              '',
              'settings',
              'faq'
            ]
          }
        ]
      },
    },

    plugins: [
      '@vuepress/plugin-back-to-top'
    ]
  }
