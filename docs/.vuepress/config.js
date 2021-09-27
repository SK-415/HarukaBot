module.exports = {
  lang: 'zh-CN',
  title: 'HarukaBot',
  description: '哔哩哔哩消息推送 QQ 机器人',
  head: [
    ['link', { rel: 'icon', href: '/logo.png' }],
    ['link', {rel: 'manifest', href: '/manifest.json'}],
    ['meta', { name: 'theme-color', content: '#f5827e'}]
  ],
  themeConfig: {
    logo: '/logo.png',
    repo: 'SK-415/HarukaBot',
    docsDir: 'docs',
    docsBranch: 'dev',
    editLinkText: '在 GitHub 上编辑此页',
    lastUpdatedText: '上次更新',
    contributorsText: '贡献者',
    tip: '提示',
    warning: '注意',
    danger: '警告',
    notFound: '什么都没找到',
    backToHome: '返回主页',
    toggleDarkMode: '切换夜间模式',
    navbar: [
      // { text: '主页', link: '/' },
      { text: '安装', link: '/install/' },
      { text: '小小白白话文', link: '/level-0/'},
      { text: '功能列表', link: '/usage/' },
      { text: '常见问题', link: '/faq/' },
      { text: '关于', link: '/about/' },
    ],
    sidebar: {
      '/install/': [
        {
          text: '安装',
          children: [
            '/install/',
            '/install/install-go-cqhttp',
            '/install/install-HarukaBot',
            '/install/congrats'
          ]
        }
      ],
      '/usage/': [
        {
          text: '使用帮助',
          children: [
            '/usage/',
            '/usage/settings',
          ]
        }
      ],
      '/level-0/':[
        {
          title: '小小白白话文',
          children: [
            '/level-0/',
            '/level-0/ch01',
            '/level-0/ch02',
            '/level-0/ch03',
            '/level-0/ch04'
          ]
        }
      ],
    },
  },
  plugins: [
    [
      '@vuepress/plugin-pwa',
      {
        skipWaiting: true,
      }
    ],
    // [
    //   '@vuepress/plugin-pwa-popup',
    //   {
    //     message: '发现新内容可用',
    //     buttonText: '刷新',
    //   }
    // ],
    [
      '@vuepress/plugin-shiki',
      {
        theme: 'dark-plus',
      }
    ],
    [
      '@vuepress/plugin-docsearch',
      {
        apiKey: 'b42f3ac623cf606bb9ea15b3e8c888d0',
        indexName: 'haruka-bot',
        placeholder: '搜索文档',
      }
    ]
  ]
}
