module.exports = {
    title: 'HarukaBot',
    description: '一个推送 B站 信息的 QQ 机器人',
    head: [
      ['link', { rel: 'icon', href: '/logo.png' }]
    ],
    themeConfig: {
      logo: '/logo.png',
      repo: 'SK-415/HarukaBot',
      docsRepo: 'SK-415/HarukaBot-docs',
      docsDir: 'docs',
      docsBranch: 'main',
      editLinks: true,
      editLinkText: '在 GitHub 上编辑此页',
      nav: [
        { text: '主页', link: '/' },
        { text: '安装方法', link: '/install/' },
        { text: '功能列表', link: '/features/' },
        { text: '常见问题', link: '/usage/faq/' },
        { 
          text: '关于', 
          items: [
            { text: '关于项目', link: '/about/' },
          ]
        }
      ],
      sidebar: {
        '/install/': [
          {
            title: '安装方法',
            collapsable: false,
            sidebar: 'auto',
            children: [
              '',
              'install-go-cqhttp',
              'install-HarukaBot'
            ]
          }
        ]
      },
      lastUpdated: '上次更新'
    }
  }