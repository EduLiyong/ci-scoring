/* =====================================================
   词作评分系统 - JavaScript 主逻辑
   ===================================================== */

// ===== 全局状态 =====
const App = {
  currentUser: null,
  selectedCipai: null,
  cipaiList: [],
  cipaiIntros: {},
  cipaiSearchTimer: null,
  currentPage: 'home',
  worksPage: 1,
};

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuthStatus();
  await loadCipaiList();
  await loadCipaiIntros();
  renderHomeCipai();
  loadCipaiPage('');
});

// ===== 页面切换 =====
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const el = document.getElementById(`page-${name}`);
  if (el) el.classList.add('active');
  document.querySelectorAll('.nav-link').forEach(a => {
    a.classList.toggle('active', a.dataset.page === name);
  });
  App.currentPage = name;
  window.scrollTo(0, 0);

  if (name === 'compose') initComposePage();
  if (name === 'history') loadHistory(1);
  if (name === 'cipai') loadCipaiPage('');
}

// ===== 认证 =====
async function checkAuthStatus() {
  try {
    const res = await api('/api/auth/status');
    if (res.logged_in) {
      setUser(res.user);
    }
  } catch {}
}

function setUser(user) {
  App.currentUser = user;
  document.getElementById('userArea').classList.remove('hidden');
  document.getElementById('authButtons').classList.add('hidden');
  const av = document.getElementById('userAvatar');
  av.textContent = user.username.charAt(0).toUpperCase();
  document.getElementById('headerUsername').textContent = user.username;
}

function clearUser() {
  App.currentUser = null;
  document.getElementById('userArea').classList.add('hidden');
  document.getElementById('authButtons').classList.remove('hidden');
}

// 发送验证码
let codeTimer = null;
async function sendCode() {
  const phone = document.getElementById('regPhone').value.trim();
  if (!phone || phone.length !== 11 || !/^\d+$/.test(phone)) {
    showMsg('registerMsg', '请输入正确的11位手机号', 'error');
    return;
  }
  const btn = document.getElementById('sendCodeBtn');
  btn.disabled = true;
  btn.textContent = '发送中...';

  // 清除之前的倒计时
  if (codeTimer) {
    clearInterval(codeTimer);
    codeTimer = null;
  }

  let res;
  try {
    res = await api('/api/sms/send', 'POST', { phone });
  } catch (e) {
    btn.disabled = false;
    btn.textContent = '发送验证码';
    showMsg('registerMsg', '网络错误，请稍后重试', 'error');
    return;
  }

  if (res && res.success) {
    // 演示模式：显示验证码，并自动填入输入框
    if (res.demo_code) {
      const hint = document.getElementById('demoCodeHint');
      const val = document.getElementById('demoCodeVal');
      val.textContent = res.demo_code;
      hint.style.display = 'flex';
      // 自动填入验证码输入框
      const codeInput = document.getElementById('regCode');
      if (codeInput) codeInput.value = res.demo_code;
      // 滚动让提示框可见
      setTimeout(() => hint.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
    }
    showMsg('registerMsg', '✅ 验证码已获取，已自动填入输入框', 'success');
    // 倒计时60秒
    let t = 60;
    btn.textContent = `${t}s 后重发`;
    codeTimer = setInterval(() => {
      t--;
      if (t <= 0) {
        clearInterval(codeTimer);
        codeTimer = null;
        btn.disabled = false;
        btn.textContent = '重新发送';
      } else {
        btn.textContent = `${t}s 后重发`;
      }
    }, 1000);
  } else {
    btn.disabled = false;
    btn.textContent = '发送验证码';
    showMsg('registerMsg', (res && res.message) || '发送失败，请重试', 'error');
  }
}

// 注册
async function doRegister() {
  const username = document.getElementById('regUsername').value.trim();
  const phone = document.getElementById('regPhone').value.trim();
  const code = document.getElementById('regCode').value.trim();
  const password = document.getElementById('regPassword').value;
  const password2 = document.getElementById('regPassword2').value;

  if (!username) return showMsg('registerMsg', '请输入用户名', 'error');
  if (!phone) return showMsg('registerMsg', '请输入手机号', 'error');
  if (!code) return showMsg('registerMsg', '请输入验证码', 'error');
  if (!password) return showMsg('registerMsg', '请输入密码', 'error');
  if (password !== password2) return showMsg('registerMsg', '两次密码不一致', 'error');

  const res = await api('/api/auth/register', 'POST', { username, phone, code, password });
  if (res.success) {
    closeModal('registerModal');
    setUser(res.user);
    toast('注册成功，欢迎 ' + res.user.username + '！');
  } else {
    showMsg('registerMsg', res.message, 'error');
  }
}

// 登录
async function doLogin() {
  const login = document.getElementById('loginField').value.trim();
  const password = document.getElementById('loginPassword').value;
  if (!login || !password) return showMsg('loginMsg', '请输入用户名/手机号和密码', 'error');
  const res = await api('/api/auth/login', 'POST', { login, password });
  if (res.success) {
    closeModal('loginModal');
    setUser(res.user);
    toast('欢迎回来，' + res.user.username + '！');
    if (App.currentPage === 'history') loadHistory(1);
  } else {
    showMsg('loginMsg', res.message, 'error');
  }
}

// 退出登录
async function doLogout() {
  await api('/api/auth/logout', 'POST');
  clearUser();
  toast('已退出登录');
  showPage('home');
}

// ===== 词牌 =====
async function loadCipaiList() {
  const res = await api('/api/cipai/list');
  if (res.success) App.cipaiList = res.data;
}

async function loadCipaiIntros() {
  const res = await api('/api/cipai/all-intros');
  if (res.success) App.cipaiIntros = res.data;
}

function renderHomeCipai() {
  const el = document.getElementById('homeCipaiTags');
  if (!el) return;
  const preview = App.cipaiList.slice(0, 20);
  el.innerHTML = preview.map(c => `
    <span class="cipai-tag-item" onclick="selectCipaiFromHome(${c.id},'${c.name}')">${c.name}</span>
  `).join('');
}

function selectCipaiFromHome(id, name) {
  showPage('score');
  setTimeout(() => selectCipai(App.cipaiList.find(c => c.id === id)), 200);
}

// 词牌搜索（防抖）
function searchCipai(keyword) {
  clearTimeout(App.cipaiSearchTimer);
  App.cipaiSearchTimer = setTimeout(async () => {
    if (!keyword.trim()) {
      hideDropdown();
      return;
    }
    const res = await api(`/api/cipai/list?q=${encodeURIComponent(keyword)}`);
    renderCipaiDropdown(res.data || []);
  }, 200);
}

function renderCipaiDropdown(list) {
  const dd = document.getElementById('cipaiDropdown');
  if (!list || list.length === 0) {
    dd.innerHTML = '<div style="padding:12px 16px;color:#8a7a5e;font-size:14px">未找到相关词牌</div>';
    dd.classList.remove('hidden');
    return;
  }
  dd.innerHTML = list.map(c => `
    <div class="cipai-option" onclick="selectCipai(${JSON.stringify(c).replace(/"/g, '&quot;')})">
      <span class="cipai-option-name">${c.name}</span>
      <span class="cipai-option-meta">${c.dynasty || ''}·${c.description ? c.description.substring(0, 20) : ''}</span>
    </div>
  `).join('');
  dd.classList.remove('hidden');
}

function selectCipai(cipai) {
  App.selectedCipai = cipai;
  document.getElementById('cipaiSearch').value = '';
  hideDropdown();
  document.getElementById('selectedCipai').classList.remove('hidden');
  document.getElementById('selectedCipaiName').textContent = cipai.name;
  document.getElementById('selectedCipaiDesc').textContent = cipai.description || '';

  // 切换词牌时清除上一次的韵脚数据
  ComposeData.rhymeGroups = [];
  ComposeData.rhymeGroupData = {};
  document.getElementById('rhymeHint').style.display = 'none';
  const rhymeContent = document.getElementById('rhymeHintContent');
  if (rhymeContent) rhymeContent.innerHTML = '';
}

function clearCipai() {
  App.selectedCipai = null;
  document.getElementById('cipaiSearch').value = '';
  document.getElementById('selectedCipai').classList.add('hidden');
}

function hideDropdown() {
  document.getElementById('cipaiDropdown').classList.add('hidden');
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.cipai-selector')) hideDropdown();
});

// 词牌大全页
function loadCipaiPage(keyword) {
  clearTimeout(App.cipaiSearchTimer);
  App.cipaiSearchTimer = setTimeout(async () => {
    const res = await api(`/api/cipai/list?q=${encodeURIComponent(keyword || '')}`);
    const grid = document.getElementById('cipaiGrid');
    if (!grid) return;
    grid.innerHTML = (res.data || []).map(c => `
      <div class="cipai-card" onclick="chooseCipaiForScore(${c.id})">
        <div class="cipai-card-name">${c.name}</div>
        <div class="cipai-card-dynasty">${c.dynasty || ''}词</div>
        <div class="cipai-card-desc">${c.description || ''}</div>
        ${c.alias && c.alias.length ? `<div style="font-size:12px;color:#8a7a5e;margin-top:6px">又名：${c.alias.join('、')}</div>` : ''}
        <div class="cipai-card-actions">
          <span class="cipai-card-btn" onclick="showRepWorks(${c.id}, event)">
            <i class="fa fa-book-open"></i> 代表作
          </span>
          <span class="cipai-card-btn cipai-card-btn-primary">用此词牌评分 →</span>
        </div>
      </div>
    `).join('');
  }, 200);
}

function chooseCipaiForScore(cipaiId) {
  const cipai = App.cipaiList.find(c => c.id === cipaiId);
  if (cipai) {
    showPage('score');
    setTimeout(() => selectCipai(cipai), 100);
  }
}

// ===== 作者简介功能（全局） =====
const _authorBioCache = {};

function showAuthorBio(authorName) {
  if (!authorName || authorName === '佚名' || authorName === '无名氏') return;

  // 如果缓存中有，直接显示
  if (_authorBioCache[authorName]) {
    _renderAuthorBioModal(authorName, _authorBioCache[authorName]);
    return;
  }

  // 从API获取
  fetch(`/api/authors/${encodeURIComponent(authorName)}/bio`)
    .then(r => r.json())
    .then(data => {
      if (data.success && data.bio) {
        _authorBioCache[authorName] = data.bio;
        _renderAuthorBioModal(authorName, data.bio);
      }
    })
    .catch(() => {});
}

function _renderAuthorBioModal(name, bio) {
  const modal = document.getElementById('authorBioModal');
  const body = document.getElementById('authorBioModalBody');
  document.getElementById('authorBioModalName').textContent = name;
  body.innerHTML = `<div class="author-bio-text">${bio}</div>`;
  modal.classList.remove('hidden');
}

function closeAuthorBioModal() {
  document.getElementById('authorBioModal').classList.add('hidden');
}

// 词牌代表作
async function showRepWorks(cipaiId, e) {
  e.stopPropagation();
  try {
    const res = await api(`/api/cipai/${cipaiId}/representatives`);
    if (!res || !res.success) {
      showToast('加载代表作失败: ' + (res?.message || '网络错误'), 'error');
      return;
    }
    const data = res.data;
    document.getElementById('repModalTitle').innerHTML = `<i class="fa fa-book-open"></i> ${data.name} · 代表作`;

    let html = '';

    // 词牌解说区域
    const intro = App.cipaiIntros[cipaiId];
    if (intro) {
      html += `
      <div class="rep-intro-section">
        <div class="rep-intro-header">
          <i class="fa fa-info-circle"></i> 词牌解说
        </div>
        <div class="rep-intro-content">
          <div class="rep-intro-item">
            <div class="rep-intro-label"><i class="fa fa-history"></i> 词牌来源</div>
            <div class="rep-intro-text">${intro.origin || '暂无说明'}</div>
          </div>
          <div class="rep-intro-item">
            <div class="rep-intro-label"><i class="fa fa-music"></i> 音律特点</div>
            <div class="rep-intro-text">${intro.rhythm || '暂无说明'}</div>
          </div>
          <div class="rep-intro-item">
            <div class="rep-intro-label"><i class="fa fa-leaf"></i> 用韵特点</div>
            <div class="rep-intro-text">${intro.rhyme || '暂无说明'}</div>
          </div>
          <div class="rep-intro-item">
            <div class="rep-intro-label"><i class="fa fa-th-large"></i> 结构说明</div>
            <div class="rep-intro-text">${intro.structure || '暂无说明'}</div>
          </div>
        </div>
      </div>`;
    }

    // 作者字号格式化函数
    function fmtAuthor(w) {
      let name = w.author || '佚名';
      let extra = [];
      if (w.zi) extra.push('字' + w.zi);
      if (w.hao) extra.push('号' + w.hao);
      const clickable = name !== '佚名' && name !== '无名氏';
      const nameHtml = clickable
        ? `<span class="rep-work-author author-bio-link" onclick="event.stopPropagation(); showAuthorBio('${name.replace(/'/g, "\\'")}')">${name}</span>`
        : `<span class="rep-work-author">${name}</span>`;
      if (extra.length > 0) {
        return `${nameHtml}<span class="rep-work-zi-hao">（${extra.join('，')}）</span>`;
      }
      return nameHtml;
    }

    // 存储当前数据和词牌ID供编辑使用
    window._repWorksData = data;
    window._repCipaiId = cipaiId;
    const isEdu = App.currentUser && App.currentUser.username.toLowerCase() === 'edu';

    // 正体代表作
    if (data.main && data.main.length > 0) {
      html += `<div class="rep-section">
        <div class="rep-section-title">正体代表作 ${isEdu ? '<button class="rep-add-btn" onclick="addRepWork(\'main\')" title="新增正体代表作"><i class="fa fa-plus"></i></button>' : ''}</div>
        ${data.main.map((w, idx) => `
          <div class="rep-work">
            <div class="rep-work-header">
              <span class="rep-work-title">${w.title || '无题'}</span>
              ${w.dynasty ? `<span class="rep-work-dynasty">${w.dynasty}</span>` : ''}
              ${fmtAuthor(w)}
              ${isEdu ? `<button class="rep-edit-btn" onclick="editRepWork(${idx}, 'main')"><i class="fa fa-edit"></i> 编辑</button>` : ''}
            </div>
            ${w.preface ? `<div class="rep-work-preface">${w.preface}</div>` : ''}
            <div class="rep-work-text">${(w.text || '').replace(/\n/g, '<br>')}</div>
          </div>
        `).join('')}
      </div>`;
    } else if (isEdu) {
      // 如果没有正体代表作，但用户是Edu，也显示一个添加按钮
      html += `<div class="rep-section">
        <div class="rep-section-title">正体代表作 <button class="rep-add-btn" onclick="addRepWork('main')" title="新增正体代表作"><i class="fa fa-plus"></i></button></div>
        <div class="rep-empty"><i class="fa fa-inbox"></i> 暂无正体代表作，点击加号添加</div>
      </div>`;
    }

    // 变体代表作
    if (data.variants && data.variants.length > 0) {
      data.variants.forEach((v, vIdx) => {
        if (!v.works || v.works.length === 0) return;
        html += `<div class="rep-section">
          <div class="rep-section-title">变体代表作 · ${v.name || ''} ${isEdu ? `<button class="rep-add-btn" onclick="addRepWork('variant', ${vIdx})" title="新增变体代表作"><i class="fa fa-plus"></i></button>` : ''}</div>
          ${v.works.map((w, wIdx) => `
            <div class="rep-work">
              <div class="rep-work-header">
                <span class="rep-work-title">${w.title || '无题'}</span>
                ${w.dynasty ? `<span class="rep-work-dynasty">${w.dynasty}</span>` : ''}
                ${fmtAuthor(w)}
                ${isEdu ? `<button class="rep-edit-btn" onclick="editRepWork(${wIdx}, 'variant', ${vIdx})"><i class="fa fa-edit"></i> 编辑</button>` : ''}
              </div>
              ${w.preface ? `<div class="rep-work-preface">${w.preface}</div>` : ''}
              <div class="rep-work-text">${(w.text || '').replace(/\n/g, '<br>')}</div>
            </div>
          `).join('')}
        </div>`;
      });
    }

    if (!html) {
      html = '<div class="rep-empty"><i class="fa fa-inbox"></i> 暂无代表作数据</div>';
    }

    document.getElementById('repModalBody').innerHTML = html;
    showModal('repModal');
  } catch(err) {
    showToast('加载代表作时出错: ' + err.message, 'error');
    console.error('showRepWorks error:', err);
  }
}

// 编辑代表作
function editRepWork(index, type, variantIndex) {
  const data = window._repWorksData;
  const cipaiId = window._repCipaiId;
  
  let work;
  if (type === 'variant') {
    work = data.variants[variantIndex].works[index];
  } else {
    work = data.main[index];
  }
  
  // 填充编辑弹窗
  document.getElementById('editWorkTitle').value = work.title || '';
  document.getElementById('editWorkAuthor').value = work.author || '';
  document.getElementById('editWorkDynasty').value = work.dynasty || '';
  document.getElementById('editWorkZi').value = work.zi || '';
  document.getElementById('editWorkHao').value = work.hao || '';
  document.getElementById('editWorkText').value = work.text || '';
  
  // 保存索引信息
  window._editWorkIndex = index;
  window._editWorkType = type;
  window._editVariantIndex = (variantIndex !== undefined && variantIndex !== null) ? variantIndex : 0;
  window._editCipaiId = cipaiId;
  
  // 显示编辑弹窗
  showModal('editRepModal');
}

// 保存编辑的代表作
async function saveRepWork() {
  const title = document.getElementById('editWorkTitle').value.trim();
  const author = document.getElementById('editWorkAuthor').value.trim();
  const dynasty = document.getElementById('editWorkDynasty').value.trim();
  const zi = document.getElementById('editWorkZi').value.trim();
  const hao = document.getElementById('editWorkHao').value.trim();
  const text = document.getElementById('editWorkText').value;

  console.log('saveRepWork called', { title, author, dynasty, cipaiId: window._editCipaiId, workIndex: window._editWorkIndex });

  if (!title) return toast('请输入作品标题', 'error');
  if (!author) return toast('请输入作者', 'error');
  if (!dynasty) return toast('请输入朝代', 'error');
  if (!text) return toast('请输入词文', 'error');

  const workData = { title, author, dynasty, zi, hao, text, type: window._editWorkType, variant_index: window._editVariantIndex };
  const url = `/api/cipai/${window._editCipaiId}/representatives/${window._editWorkIndex}`;
  console.log('PUT url:', url, 'data:', workData);

  try {
    const res = await api(url, 'PUT', workData);
    console.log('PUT response:', res);
    if (res && res.success) {
      toast('保存成功', 'success');
      closeModal('editRepModal');
      // 刷新代表作列表
      const event = { stopPropagation: () => {} };
      showRepWorks(window._editCipaiId, event);
    } else {
      toast('保存失败: ' + (res?.message || '未知错误'), 'error');
    }
  } catch(err) {
    console.error('PUT error:', err);
    toast('保存失败: ' + err.message, 'error');
  }
}

// 新增代表作
function addRepWork(type, variantIndex = 0) {
  // 保存新增类型信息
  window._addWorkType = type;
  window._addVariantIndex = variantIndex;
  window._addCipaiId = window._repCipaiId;
  
  // 清空表单
  document.getElementById('addWorkTitle').value = '';
  document.getElementById('addWorkAuthor').value = '';
  document.getElementById('addWorkDynasty').value = '';
  document.getElementById('addWorkZi').value = '';
  document.getElementById('addWorkHao').value = '';
  document.getElementById('addWorkText').value = '';
  
  // 显示新增弹窗
  showModal('addRepModal');
}

// 保存新增的代表作
async function saveNewRepWork() {
  const title = document.getElementById('addWorkTitle').value.trim();
  const author = document.getElementById('addWorkAuthor').value.trim();
  const dynasty = document.getElementById('addWorkDynasty').value.trim();
  const zi = document.getElementById('addWorkZi').value.trim();
  const hao = document.getElementById('addWorkHao').value.trim();
  const text = document.getElementById('addWorkText').value;

  if (!title) return toast('请输入作品标题', 'error');
  if (!author) return toast('请输入作者', 'error');
  if (!dynasty) return toast('请输入朝代', 'error');
  if (!text) return toast('请输入词文', 'error');

  const workData = { 
    title, 
    author, 
    dynasty, 
    zi, 
    hao, 
    text, 
    type: window._addWorkType, 
    variant_index: window._addVariantIndex 
  };
  
  const url = `/api/cipai/${window._addCipaiId}/representatives`;

  try {
    const res = await api(url, 'POST', workData);
    if (res && res.success) {
      toast('新增成功', 'success');
      closeModal('addRepModal');
      // 刷新代表作列表
      const event = { stopPropagation: () => {} };
      showRepWorks(window._addCipaiId, event);
    } else {
      toast('新增失败: ' + (res?.message || '未知错误'), 'error');
    }
  } catch(err) {
    toast('新增失败: ' + err.message, 'error');
  }
}

// ===== 字数统计 =====
function updateCharCount() {
  const content = document.getElementById('poemContent').value;
  const count = content.replace(/[^\u4e00-\u9fff]/g, '').length;
  document.getElementById('charCount').textContent = count;
}

// ===== 重复校验相关 =====
let pendingScoreData = null;  // 暂存待评分数据

function showDuplicateModal(work) {
  App.duplicateWork = work;
  document.getElementById('dupWorkTitle').textContent = work.title || '无标题';
  document.getElementById('dupWorkCipai').textContent = work.cipai_name;
  document.getElementById('dupWorkScore').textContent = work.total_score + '分';
  document.getElementById('dupWorkCount').textContent = '第' + work.score_count + '次';
  document.getElementById('dupWorkDate').textContent = '最后更新：' + work.updated_at;
  showModal('duplicateModal');
}

function viewDuplicateWork() {
  closeModal('duplicateModal');
  if (App.duplicateWork) {
    viewWork(App.duplicateWork.id);
  }
}

async function rescoreDuplicate() {
  closeModal('duplicateModal');
  if (!pendingScoreData) return;
  
  // 强制重新评分（使用已有作品的work_id）
  const workId = App.duplicateWork ? App.duplicateWork.id : null;
  await doScore(pendingScoreData, workId);
}

// ===== 评分逻辑 =====
async function submitScore() {
  if (!App.currentUser) {
    showModal('loginModal');
    toast('请先登录后再评分');
    return;
  }
  if (!App.selectedCipai) {
    toast('请先选择词牌名称');
    return;
  }
  const content = document.getElementById('poemContent').value.trim();
  if (!content) {
    toast('请输入词作内容');
    return;
  }

  const title = document.getElementById('poemTitle').value.trim();
  const workId = document.getElementById('editWorkId').value || null;

  // 暂存数据用于后续可能的重复处理
  pendingScoreData = {
    cipai_id: App.selectedCipai.id,
    content,
    title,
    work_id: workId ? parseInt(workId) : null
  };

  // 如果是编辑已有作品，直接评分，不做重复检测
  if (workId) {
    await doScore(pendingScoreData, workId);
    return;
  }

  // 先检查是否有重复作品
  showLoading(true);
  try {
    const checkRes = await api('/api/score/check-duplicate', 'POST', {
      cipai_id: App.selectedCipai.id,
      content
    });

    if (checkRes.success && checkRes.is_duplicate) {
      showLoading(false);
      showDuplicateModal(checkRes.existing_work);
      return;
    }

    // 没有重复，继续评分
    await doScore(pendingScoreData);
  } catch (e) {
    showLoading(false);
    toast('请求失败，请检查网络', 'error');
  }
}

async function doScore(data, existingWorkId = null) {
  // 显示加载
  showLoading(true);

  // 加载步骤动画
  let step = 1;
  const stepTimer = setInterval(() => {
    document.querySelectorAll('.loading-step').forEach((el, i) => {
      el.classList.toggle('active', i + 1 === step);
    });
    if (step < 3) step++;
  }, 800);

  try {
    const payload = {
      cipai_id: data.cipai_id,
      content: data.content,
      title: data.title
    };
    
    // 如果是重新评分已有作品
    if (existingWorkId) {
      payload.work_id = existingWorkId;
    }

    const res = await api('/api/score', 'POST', payload);

    clearInterval(stepTimer);
    showLoading(false);

    if (res.success) {
      if (res.is_duplicate) {
        // 再次检测到重复（理论上不会走到这里，因为前面已检查）
        showDuplicateModal(res.existing_work);
      } else {
        renderScoreResult(res.data);
        // 清空暂存数据
        pendingScoreData = null;
        App.duplicateWork = null;
      }
    } else {
      toast('评分失败：' + res.message, 'error');
    }
  } catch (e) {
    clearInterval(stepTimer);
    showLoading(false);
    toast('请求失败，请检查网络', 'error');
  }
}

function showLoading(show) {
  document.getElementById('resultPlaceholder').classList.add('hidden');
  document.getElementById('scoreResult').classList.add('hidden');
  const loading = document.getElementById('scoreLoading');
  if (show) {
    loading.classList.remove('hidden');
    // 重置步骤
    document.querySelectorAll('.loading-step').forEach((el, i) => {
      el.classList.toggle('active', i === 0);
    });
  } else {
    loading.classList.add('hidden');
  }
}

function renderScoreResult(data) {
  const el = document.getElementById('scoreResult');
  el.classList.remove('hidden');

  // 标题
  document.getElementById('resultTitle').textContent = data.title || '评分结果';
  document.getElementById('resultCipaiName').textContent = data.cipai_name;

  // 总分动画
  const total = data.total_score;
  animateScore(total);

  // 分项
  document.getElementById('rhythmScoreVal').textContent = data.rhythm_score;
  document.getElementById('yijingScoreVal').textContent = data.yijing_score;
  setTimeout(() => {
    document.getElementById('rhythmBar').style.width = (data.rhythm_score / 50 * 100) + '%';
    document.getElementById('yijingBar').style.width = (data.yijing_score / 50 * 100) + '%';
  }, 300);

  // 等级
  const grade = getGrade(total);
  const badge = document.getElementById('gradeBadge');
  badge.textContent = grade.label;
  badge.style.background = grade.bg;
  badge.style.color = grade.color;

  // 韵律详情
  const rd = data.rhythm_detail;
  document.getElementById('matchedPattern').textContent = rd.matched_pattern || '-';
  document.getElementById('patternType').textContent = rd.pattern_type || '-';
  document.getElementById('matchRate').textContent = rd.match_rate ? rd.match_rate + '%' : '-';

  // 声调分析
  renderToneAnalysis(rd.tone_detail);

  // 意境详情
  renderYijingDetail(data.yijing_detail);

  // 展开详情
  setTimeout(() => {
    toggleDetail('rhythmDetail');
    toggleDetail('yijingDetail');
  }, 300);
}

function animateScore(target) {
  let current = 0;
  const circle = document.getElementById('scoreCirclePath');
  const numEl = document.getElementById('totalScoreNum');
  const circumference = 339.3;
  const step = target / 60;

  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    numEl.textContent = Math.round(current);
    const offset = circumference * (1 - current / 100);
    circle.style.strokeDashoffset = offset;
    if (current >= target) clearInterval(timer);
  }, 16);
}

function getGrade(score) {
  if (score >= 90) return { label: '🏆 词中翘楚 · 传世佳作', bg: 'linear-gradient(135deg,#f6d365,#fda085)', color: '#7a4000' };
  if (score >= 80) return { label: '🌟 格律精工 · 意境深远', bg: 'linear-gradient(135deg,#89f7fe,#66a6ff)', color: '#1a3a6a' };
  if (score >= 70) return { label: '✨ 词笔清秀 · 可圈可点', bg: 'linear-gradient(135deg,#84fab0,#8fd3f4)', color: '#1a4a3a' };
  if (score >= 60) return { label: '📝 初有气韵 · 尚待打磨', bg: 'linear-gradient(135deg,#ffecd2,#fcb69f)', color: '#7a4020' };
  return { label: '🌱 方入门径 · 继续努力', bg: '#f0e8d0', color: '#5a4a2e' };
}

function renderToneAnalysis(toneData) {
  const el = document.getElementById('toneAnalysis');
  if (!toneData || toneData.length === 0) {
    el.innerHTML = '';
    return;
  }

  // 统计错误字数
  let totalMismatch = 0;
  toneData.forEach(s => s.analysis.forEach(c => { if (c.match === 'mismatch') totalMismatch++; }));

  el.innerHTML = `
    <div class="tone-legend">
      <span class="legend-item"><span class="legend-dot match"></span>符合</span>
      <span class="legend-item"><span class="legend-dot mismatch"></span>不符（虚线框）</span>
      <span class="legend-item"><span class="legend-dot flexible"></span>可平可仄</span>
      <span class="legend-item"><span class="legend-dot rhyme"></span>韵脚</span>
    </div>
    ${totalMismatch > 0
      ? `<div class="tone-summary-warn"><i class="fa fa-exclamation-circle"></i> 共 <b>${totalMismatch}</b> 处平仄不符（黄色虚线框标注）</div>`
      : `<div class="tone-summary-ok"><i class="fa fa-check-circle"></i> 全部平仄符合所选格律</div>`
    }
    ${toneData.map((sent, i) => {
      const hasMismatch = sent.analysis.some(c => c.match === 'mismatch');
      return `
      <div class="tone-sentence ${hasMismatch ? 'has-mismatch' : ''}">
        <div class="tone-sentence-label">第${i + 1}句</div>
        <div class="tone-chars">
          ${sent.analysis.map(c => {
            // unknown 字按 flexible 样式展示（保守处理，不算错）
            const matchCls = c.match === 'unknown' ? 'flexible' : (c.match || 'flexible');
            // 显示声调：unknown时显示"中"，其余原样
            const toneLabel = c.tone || '中';
            // 期望格律作为 tooltip
            const expText = c.expected && c.expected !== '-' ? c.expected : '';
            const titleText = expText
              ? `实际：${toneLabel}  期望：${expText}`
              : `实际：${toneLabel}`;
            return `<div class="tone-char tone-${matchCls}" title="${titleText}">
              <span class="tone-char-text">${c.char}</span>
              <span class="tone-char-label">${toneLabel}</span>
            </div>`;
          }).join('')}
        </div>
      </div>`;
    }).join('')}
  `;
}


function renderYijingDetail(yd) {
  if (!yd) return;
  const dims = yd.dimensions || {};
  const dimNames = {
    imagery: '意象运用',
    emotion: '情感表达',
    artistic_conception: '意境营造',
    language: '语言美感'
  };
  const dimEl = document.getElementById('yijingDims');
  dimEl.innerHTML = Object.entries(dimNames).map(([key, name]) => {
    const d = dims[key] || {};
    return `
      <div class="yijing-dim">
        <div class="yijing-dim-header">
          <span class="yijing-dim-name">${name}</span>
          <span class="yijing-dim-score">${d.score || 0}</span>
        </div>
        <div class="yijing-dim-comment">${d.comment || ''}</div>
      </div>
    `;
  }).join('');

  document.getElementById('yijingComment').innerHTML = yd.overall_comment || '';

  const hl = yd.highlights || [];
  const hlEl = document.getElementById('yijingHighlights');
  if (hl.length) {
    hlEl.innerHTML = `<h4>✦ 亮点</h4>${hl.map(h => `<div class="highlight-item">${h}</div>`).join('')}`;
  } else hlEl.innerHTML = '';

  const sg = yd.suggestions || [];
  const sgEl = document.getElementById('yijingSuggestions');
  if (sg.length) {
    sgEl.innerHTML = `<h4>→ 改进建议</h4>${sg.map(s => `<div class="suggestion-item">${s}</div>`).join('')}`;
  } else sgEl.innerHTML = '';

  const notice = document.getElementById('llmNotice');
  if (yd.source === 'mock') {
    notice.textContent = '⚠️ 当前为演示模式，配置大模型API Key后可获得真实AI意境评分';
    notice.style.display = 'block';
  } else if (yd.source === 'llm') {
    notice.style.display = 'none';
  } else if (yd.source === 'error') {
    notice.textContent = '⚠️ ' + (yd.error || '意境评分服务暂时不可用');
    notice.style.display = 'block';
  }
}

function clearScoreForm() {
  document.getElementById('poemTitle').value = '';
  document.getElementById('poemContent').value = '';
  document.getElementById('editWorkId').value = '';
  document.getElementById('charCount').textContent = '0';
  clearCipai();
  document.getElementById('scoreResult').classList.add('hidden');
  document.getElementById('scoreLoading').classList.add('hidden');
  document.getElementById('resultPlaceholder').classList.remove('hidden');
}

// 详情折叠
function toggleDetail(id) {
  const el = document.getElementById(id);
  const toggleEl = document.getElementById(id + 'Toggle');
  if (!el) return;
  el.classList.toggle('open');
  if (toggleEl) toggleEl.classList.toggle('open', el.classList.contains('open'));
}

function gotoScore() {
  if (!App.currentUser) {
    showModal('loginModal');
    return;
  }
  showPage('score');
}

// ===== 历史作品 =====
async function loadHistory(page) {
  App.worksPage = page || 1;
  if (!App.currentUser) {
    document.getElementById('historyLogin').style.display = 'block';
    document.getElementById('historyContent').style.display = 'none';
    return;
  }
  document.getElementById('historyLogin').style.display = 'none';
  document.getElementById('historyContent').style.display = 'block';

  const res = await api(`/api/works?page=${App.worksPage}&per_page=9`);
  if (!res.success) return;

  document.getElementById('historyStats').textContent = `共 ${res.total} 件作品`;

  const grid = document.getElementById('worksGrid');
  const empty = document.getElementById('historyEmpty');

  if (!res.data || res.data.length === 0) {
    empty.style.display = 'flex';
    grid.innerHTML = '';
    document.getElementById('pagination').innerHTML = '';
    return;
  }
  empty.style.display = 'none';
  grid.innerHTML = res.data.map(w => `
    <div class="work-card">
      <div class="work-card-header">
        <div class="work-title">${escHtml(w.title)}</div>
        <span class="work-cipai">${escHtml(w.cipai_name)}</span>
      </div>
      <div class="work-content-preview">${escHtml(w.content)}</div>
      <div class="work-scores">
        <div class="work-total-score">${w.total_score}</div>
        <div class="work-score-unit">分</div>
        <div class="work-sub-scores">
          <span>韵律：${w.rhythm_score}/50</span>
          <span>意境：${w.yijing_score}/50</span>
        </div>
      </div>
      <div class="work-card-footer">
        <span class="work-date">${w.updated_at} · 第${w.score_count}次评分</span>
        <div class="work-actions">
          <button class="work-action-btn" onclick="event.stopPropagation();viewWork(${w.id})">查看</button>
          <button class="work-action-btn" onclick="event.stopPropagation();editWork(${w.id})">修改评分</button>
          <button class="work-action-btn danger" onclick="event.stopPropagation();deleteWork(${w.id})">删除</button>
        </div>
      </div>
    </div>
  `).join('');

  // 分页
  renderPagination(res.pages, res.page);
}

function renderPagination(totalPages, currentPage) {
  const el = document.getElementById('pagination');
  if (totalPages <= 1) { el.innerHTML = ''; return; }
  let html = '';
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="loadHistory(${i})">${i}</button>`;
  }
  el.innerHTML = html;
}

async function viewWork(id) {
  const res = await api(`/api/works/${id}`);
  if (!res.success) return;
  const w = res.data;
  const body = document.getElementById('workDetailBody');
  document.getElementById('detailModalTitle').textContent = w.title;

  const yd = w.yijing_detail || {};
  const rd = w.rhythm_detail || {};

  body.innerHTML = `
    <div class="result-cipai" style="margin-bottom:12px">${escHtml(w.cipai_name)}</div>
    <div class="detail-poem-content">${escHtml(w.content)}</div>
    <div class="detail-scores-row">
      <div class="detail-score-box">
        <div class="detail-score-label">总分</div>
        <div class="detail-score-num total">${w.total_score}</div>
      </div>
      <div class="detail-score-box">
        <div class="detail-score-label">韵律分</div>
        <div class="detail-score-num">${w.rhythm_score}/50</div>
      </div>
      <div class="detail-score-box">
        <div class="detail-score-label">意境分</div>
        <div class="detail-score-num">${w.yijing_score}/50</div>
      </div>
    </div>
    ${yd.overall_comment ? `
    <div class="yijing-comment" style="margin-bottom:12px">
      ${escHtml(yd.overall_comment)}
    </div>` : ''}
    <div class="info-row">
      <span class="info-label">匹配格律：</span>
      <span class="info-value">${escHtml(rd.matched_pattern || '-')}</span>
    </div>
    <div class="info-row">
      <span class="info-label">评分次数：</span>
      <span class="info-value">第 ${w.score_count} 次</span>
    </div>
    <div class="info-row">
      <span class="info-label">最后更新：</span>
      <span class="info-value">${w.updated_at}</span>
    </div>
    <div style="display:flex;gap:12px;margin-top:16px">
      <button class="btn btn-primary" style="flex:1;justify-content:center" 
              onclick="editWork(${w.id});closeModal('workDetailModal')">
        <i class="fa fa-edit"></i> 修改并重新评分
      </button>
      <button class="btn btn-outline" style="flex:1;justify-content:center" 
              onclick="closeModal('workDetailModal')">关闭</button>
    </div>
  `;
  showModal('workDetailModal');
}

async function editWork(id) {
  const res = await api(`/api/works/${id}`);
  if (!res.success) return;
  const w = res.data;

  // 切换到评分页并填充数据
  showPage('score');
  document.getElementById('poemTitle').value = w.title;
  document.getElementById('poemContent').value = w.content;
  document.getElementById('editWorkId').value = w.id;
  document.getElementById('charCount').textContent = w.content.replace(/[^\u4e00-\u9fff]/g, '').length;

  // 选择词牌
  const cipai = App.cipaiList.find(c => c.id === w.cipai_id);
  if (cipai) selectCipai(cipai);

  // 重置右侧结果区域，避免显示上一个作品的旧评分
  document.getElementById('scoreResult').classList.add('hidden');
  document.getElementById('scoreLoading').classList.add('hidden');
  document.getElementById('resultPlaceholder').classList.remove('hidden');

  toast('已加载作品，修改后点击"开始评分"重新评分');
}

async function deleteWork(id) {
  if (!confirm('确定要删除这件作品吗？')) return;
  const res = await api(`/api/works/${id}`, 'DELETE');
  if (res.success) {
    toast('已删除');
    loadHistory(App.worksPage);
  } else {
    toast('删除失败：' + res.message, 'error');
  }
}

// ===== LLM配置 =====
async function showLLMConfig() {
  const res = await api('/api/config/llm');
  if (res.success) {
    const d = res.data;
    document.getElementById('cfgApiUrl').value = d.api_url || '';
    document.getElementById('cfgModel').value = d.model || '';
    document.getElementById('cfgApiKey').value = d.has_key ? '••••••••' : '';
  }
  showModal('llmConfigModal');
}

async function saveLLMConfig() {
  const api_url = document.getElementById('cfgApiUrl').value.trim();
  const api_key = document.getElementById('cfgApiKey').value.trim();
  const model = document.getElementById('cfgModel').value.trim();

  const payload = {};
  if (api_url) payload.api_url = api_url;
  if (api_key && !api_key.includes('•')) payload.api_key = api_key;
  if (model) payload.model = model;

  const res = await api('/api/config/llm', 'POST', payload);
  if (res.success) {
    showMsg('llmConfigMsg', '配置已保存', 'success');
    setTimeout(() => closeModal('llmConfigModal'), 1500);
  } else {
    showMsg('llmConfigMsg', res.message, 'error');
  }
}

// ===== 工具函数 =====
async function api(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include'
  };
  if (body) opts.body = JSON.stringify(body);
  console.log('api request:', method, url, body);
  try {
    const res = await fetch(url, opts);
    const data = await res.json();
    console.log('api response:', res.status, data);
    return data;
  } catch (e) {
    console.error('api error:', e);
    return { success: false, message: '网络错误' };
  }
}

function showModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('hidden');
  }
  // 打开注册弹窗时重置验证码状态
  if (id === 'registerModal') {
    const hint = document.getElementById('demoCodeHint');
    if (hint) hint.style.display = 'none';
    const btn = document.getElementById('sendCodeBtn');
    if (btn && !codeTimer) {
      btn.disabled = false;
      btn.textContent = '发送验证码';
    }
    const msg = document.getElementById('registerMsg');
    if (msg) { msg.textContent = ''; msg.className = 'msg-area'; }
  }
}
function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
  // 关闭时移除全屏状态
  const modal = document.querySelector(`#${id} .modal`);
  if (modal) modal.classList.remove('fullscreen');
}
function toggleFullscreen(modalId) {
  const modal = document.querySelector(`#${modalId} .modal`);
  if (modal) {
    modal.classList.toggle('fullscreen');
    const icon = modal.querySelector('.modal-fullscreen i');
    if (icon) {
      icon.className = modal.classList.contains('fullscreen') ? 'fa fa-compress' : 'fa fa-expand';
    }
  }
}
function switchModal(from, to) {
  closeModal(from);
  showModal(to);
}

// 点击遮罩关闭弹窗（editRepModal 除外，需要手动关闭）
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', function (e) {
    if (e.target === this && this.id !== 'editRepModal') closeModal(this.id);
  });
});

function showMsg(id, msg, type) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.className = 'msg-area msg-' + type;
}

function toast(msg, type = 'default') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast';
  if (type === 'error') t.style.background = '#c0392b';
  else t.style.background = '';
  t.classList.remove('hidden');
  setTimeout(() => t.classList.add('hidden'), 3000);
}
// showToast 是 toast 的别名
const showToast = toast;

function togglePw(id, icon) {
  const inp = document.getElementById(id);
  if (inp.type === 'password') {
    inp.type = 'text';
    icon.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
    inp.type = 'password';
    icon.classList.replace('fa-eye-slash', 'fa-eye');
  }
}

function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ===== 填词功能 =====
let ComposeData = {
  selectedCipaiId: null,
  selectedCipai: null,
  grid: null,
  rhymePositions: [],
  rhymeGroups: [],       // 韵组分组 [{index, type, positions}]
  rhymeGroupData: {},    // 按韵组独立: {groupIndex: {baseChar, yunbuDisplay, compatYunbus, yunbuChars}}
  rhymeScheme: null,     // 韵格分类信息 {type, name, desc, color, icon, rhyme_groups, is_ye_rhyme}
  userChars: {},         // 用户填写的字 {global_index: char}
  patternWorks: {},      // 缓存格律代表作 {patternIndex: [works]}
};

// 根据韵格类型获取韵脚的CSS类名
function getRhymeGroupClass(rhymeGroupIndex, isRhyme, multiGroup) {
  if (!isRhyme) return '';
  if (!multiGroup) return 'rhyme-char';
  
  const rs = ComposeData.rhymeScheme;
  const schemeType = rs ? rs.type : '';
  
  // 阕间换韵：上阕用一个颜色，下阕用另一个颜色
  if (schemeType === 'que_jian') {
    return `rhyme-char rhyme-stanza-${rhymeGroupIndex}`;
  }
  
  // 阕内换韵 / 阕内+阕间皆换韵：每个韵组用不同颜色
  if (schemeType === 'que_nei' || schemeType === 'que_nei_jian') {
    return `rhyme-char rhyme-group-${rhymeGroupIndex % 5}`;
  }
  
  // 平韵格/仄韵格：统一颜色（已有rhyme-char默认样式）
  return 'rhyme-char';
}

// 根据韵格类型获取韵组标签的CSS类名
function getRhymeGroupLabelClass(rhymeGroupIndex) {
  const rs = ComposeData.rhymeScheme;
  const schemeType = rs ? rs.type : '';
  
  if (schemeType === 'que_jian') {
    return `rhyme-group-label-stanza-${rhymeGroupIndex}`;
  }
  if (schemeType === 'que_nei' || schemeType === 'que_nei_jian') {
    return `rhyme-group-label-${rhymeGroupIndex % 5}`;
  }
  return '';
}

// 页面切换时初始化
function initComposePage() {
  if (!App.currentUser) {
    document.getElementById('composeStep1').style.display = 'none';
    document.getElementById('composeStep2').style.display = 'none';
    document.getElementById('composeLogin').style.display = 'flex';
    return;
  }
  
  document.getElementById('composeLogin').style.display = 'none';
  document.getElementById('composeStep1').style.display = 'block';
  document.getElementById('composeStep2').style.display = 'none';
  
  // 加载词牌列表
  loadComposeCipaiList();
}

// 加载词牌列表
async function loadComposeCipaiList() {
  if (!App.cipaiList || App.cipaiList.length === 0) {
    await loadCipaiList();
  }
  renderComposeCipaiGrid(App.cipaiList);
}

// 渲染词牌卡片
function renderComposeCipaiGrid(cipaiList) {
  const grid = document.getElementById('composeCipaiGrid');
  grid.innerHTML = cipaiList.map(c => {
    const patternCount = c.pattern_count || 1;
    const patternText = patternCount === 1 ? '1种格律' : `${patternCount}种格律`;
    const rs = c.rhyme_scheme;
    const rsTag = rs ? `<span class="cipai-rhyme-scheme-tag" data-scheme="${rs.type}">${rs.name}</span>` : '';
    return `
      <div class="compose-cipai-card" onclick="selectComposeCipai(${c.id})">
        <h4>${escHtml(c.name)}</h4>
        <p>${patternText} ${rsTag}</p>
      </div>
    `;
  }).join('');
}

// 搜索过滤词牌
function filterComposeCipai(keyword) {
  const filtered = App.cipaiList.filter(c => 
    c.name.toLowerCase().includes(keyword.toLowerCase())
  );
  renderComposeCipaiGrid(filtered);
}

// 选择词牌
async function selectComposeCipai(cipaiId) {
  // 高亮选中
  document.querySelectorAll('.compose-cipai-card').forEach(el => {
    el.classList.remove('selected');
  });
  event.target.closest('.compose-cipai-card').classList.add('selected');
  
  // 获取词牌基本信息
  const cipaiBasic = App.cipaiList.find(c => c.id === cipaiId);
  if (!cipaiBasic) {
    toast('词牌信息不存在', 'error');
    return;
  }
  
  // 清空之前的韵脚数据
  ComposeData.rhymeGroups = [];
  ComposeData.rhymeGroupData = {};
  ComposeData.userChars = {};
  ComposeData.patternWorks = {}; // 清空格律代表作缓存
  document.getElementById('rhymeHint').style.display = 'none';
  document.getElementById('rhymeStatus').textContent = '等待输入...';
  
  ComposeData.selectedCipaiId = cipaiId;
  
  // 检查是否需要选择格律（如果词牌有多个格律）
  if (cipaiBasic.pattern_count && cipaiBasic.pattern_count > 1) {
    // 有多个格律，需要获取完整信息
    const res = await api(`/api/cipai/${cipaiId}`);
    if (res.success) {
      ComposeData.selectedCipai = res.data;
      showPatternSelector(cipaiId, res.data);
    } else {
      toast('获取词牌信息失败', 'error');
    }
  } else {
    // 只有一个格律，直接加载
    await loadPatternGrid(cipaiId, 0);
  }
}

// 显示格律选择器
async function showPatternSelector(cipaiId, cipai) {
  document.getElementById('composeCipaiNameForPattern').textContent = cipai.name;

  // 并行加载所有格律的代表作（优化性能）
  const patterns = cipai.patterns || [];
  const promises = patterns.map((_, i) =>
    api(`/api/cipai/${cipaiId}/representatives?pattern=${i}`).catch(() => ({ success: false }))
  );

  const repResults = await Promise.all(promises);

  // 构建HTML
  let html = '';
  for (let i = 0; i < patterns.length; i++) {
    const pattern = patterns[i];
    const patternName = pattern.name || `格律${i + 1}`;
    const totalChars = pattern.total_chars || 0;
    const sentenceCount = pattern.sentences ? pattern.sentences.length : 0;

    // 获取该格律的韵格信息
    const rhymeSchemes = cipai.rhyme_schemes || [];
    const rsInfo = rhymeSchemes[i];
    const rsTag = rsInfo ? `<span class="pattern-rhyme-scheme" data-scheme="${rsInfo.type}">${rsInfo.name}</span>` : '';

    // 从并行结果中获取代表作
    const repRes = repResults[i];
    let works = [];
    if (repRes.success && repRes.data.works) {
      works = repRes.data.works.slice(0, 1); // 只显示第一首代表作
      // 缓存完整代表作数据
      ComposeData.patternWorks[i] = repRes.data.works;
    }

    html += `
      <div class="pattern-card" onclick="selectPattern(${i})">
        <div class="pattern-header">
          <h4 class="pattern-name">${patternName}${rsTag}</h4>
          <div class="pattern-info">${totalChars}字 · ${sentenceCount}句</div>
        </div>
        <div class="pattern-works">
          ${works.length > 0 ? `
            <div class="pattern-works-title">代表作品：</div>
            ${works.map((w, idx) => `
              <div class="pattern-work-item" onclick="event.stopPropagation(); showWorkDetail(${i}, ${idx})">
                <span class="work-dynasty">${w.dynasty || ''}</span>
                <span class="work-author author-bio-link" onclick="event.stopPropagation(); showAuthorBio('${(w.author || '').replace(/'/g, "\\'")}')">${w.author || ''}</span>
                <span class="work-title">《${w.title.split('·')[1] || w.title}》</span>
              </div>
            `).join('')}
          ` : '<div class="pattern-works-empty">暂无代表作</div>'}
        </div>
      </div>
    `;
  }

  document.getElementById('patternList').innerHTML = html;
  document.getElementById('composeStep1').style.display = 'none';
  document.getElementById('composeStep1_5').style.display = 'block';
  document.getElementById('composeStep2').style.display = 'none';
}

// 选择格律
async function selectPattern(patternIndex) {
  await loadPatternGrid(ComposeData.selectedCipaiId, patternIndex);
}

// 返回到词牌选择
function backToCipaiSelect() {
  document.getElementById('composeStep1').style.display = 'block';
  document.getElementById('composeStep1_5').style.display = 'none';
  document.getElementById('composeStep2').style.display = 'none';

  // 清除选中状态
  document.querySelectorAll('.compose-cipai-card').forEach(el => {
    el.classList.remove('selected');
  });
}

// 返回到格律选择
function backToPatternSelect() {
  document.getElementById('composeStep1').style.display = 'none';
  document.getElementById('composeStep1_5').style.display = 'block';
  document.getElementById('composeStep2').style.display = 'none';

  // 清除韵组 UI 显示
  document.getElementById('rhymeHint').style.display = 'none';
  const rhymeContent = document.getElementById('rhymeHintContent');
  if (rhymeContent) rhymeContent.innerHTML = '';
}

// 展开/收起代表作区域
function toggleRepWork() {
  const content = document.getElementById('composeRepContent');
  const icon = document.getElementById('repWorkToggleIcon');
  
  if (content.style.display === 'none') {
    content.style.display = 'block';
    icon.classList.remove('fa-chevron-right');
    icon.classList.add('fa-chevron-down');
  } else {
    content.style.display = 'none';
    icon.classList.remove('fa-chevron-down');
    icon.classList.add('fa-chevron-right');
  }
}

// 加载格律格子
async function loadPatternGrid(cipaiId, patternIndex) {
  const res = await api(`/api/cipai/${cipaiId}/grid?pattern=${patternIndex}`);
  if (!res.success) {
    toast('加载词牌格律失败：' + res.message, 'error');
    return;
  }
  
  ComposeData.selectedPatternIndex = patternIndex;
  ComposeData.grid = res.data.grid;
  ComposeData.rhymePositions = res.data.rhyme_positions;
  ComposeData.rhymeGroups = res.data.rhyme_groups || [];
  ComposeData.rhymeScheme = res.data.rhyme_scheme || null;
  ComposeData.lineGroups = res.data.line_groups || [];
  ComposeData.stanzaSplit = res.data.stanza_split || null;
  ComposeData.rhymeGroupData = {};
  ComposeData.userChars = {};

  // 清除韵组 UI 显示
  document.getElementById('rhymeHint').style.display = 'none';
  const rhymeContent = document.getElementById('rhymeHintContent');
  if (rhymeContent) rhymeContent.innerHTML = '';
  
  // 显示填词界面
  document.getElementById('composeCipaiName').textContent = res.data.cipai_name;
  document.getElementById('composePatternName').textContent = res.data.pattern_name;
  
  // 显示韵格标签
  const rsEl = document.getElementById('composeRhymeScheme');
  if (rsEl && ComposeData.rhymeScheme) {
    const rs = ComposeData.rhymeScheme;
    rsEl.innerHTML = `<span class="rhyme-scheme-badge" data-scheme="${rs.type}">${rs.name}</span>`;
    rsEl.title = rs.desc;
    rsEl.style.display = 'inline-block';
  } else if (rsEl) {
    rsEl.innerHTML = '';
    rsEl.style.display = 'none';
  }
  document.getElementById('composeStep1').style.display = 'none';
  document.getElementById('composeStep1_5').style.display = 'none';
  document.getElementById('composeStep2').style.display = 'block';
  
  // 单格律词牌隐藏"返回选择格律"按钮
  const backToPatternBtn = document.querySelector('#composeStep2 .compose-header button[onclick="backToPatternSelect()"]');
  if (backToPatternBtn) {
    backToPatternBtn.style.display = (res.data.total_patterns && res.data.total_patterns > 1) ? '' : 'none';
  }
  
  // 展示代表作参考（上方）
  await loadComposeRepWork(cipaiId, patternIndex);
  
  // 渲染格子（下方填词区，始终可见）
  renderComposeGrid();
}

// 加载填词界面的代表作展示
async function loadComposeRepWork(cipaiId, patternIndex) {
  const repDiv = document.getElementById('composeRepWork');
  
  // 加载代表作（优先使用缓存）
  let works = ComposeData.patternWorks[patternIndex];

  if (!works) {
    // 没有缓存，调用API
    const repRes = await api(`/api/cipai/${cipaiId}/representatives?pattern=${patternIndex}`);
    if (repRes.success && repRes.data.works) {
      works = repRes.data.works;
      ComposeData.patternWorks[patternIndex] = works;
    } else {
      works = [];
    }
  }
  
  if (works.length === 0) {
    // 没有代表作，隐藏参考区
    repDiv.style.display = 'none';
    return;
  }
  
  // 展示代表作（以较小文字展示在上方参考区）
  const contentDiv = document.getElementById('composeRepContent');
  let html = '';
  
  const lineGroups = ComposeData.lineGroups || [];
  const stanzaSplit = ComposeData.stanzaSplit;
  const grid = ComposeData.grid;
  
  // 计算上阕最后一行的索引
  let lastUpperLineIdx = -1;
  if (lineGroups.length > 0 && stanzaSplit) {
    let sentCount = 0;
    for (let li = 0; li < lineGroups.length; li++) {
      sentCount += lineGroups[li].length;
      if (sentCount >= stanzaSplit) {
        lastUpperLineIdx = li;
        break;
      }
    }
  }
  
  // 只显示第一首代表作
  const w = works[0];
  const workText = w.text || w.content || '';

  // 代表作按原文标点断句展示，不再按格律格子结构强制对齐
  // 这样可以正确显示句子的完整性（如"三十六宫都足。"不会被拆分）
  let workHtml = formatWorkContent(workText);
  
  html += `
    <div class="rep-work-item">
      <div class="rep-work-meta">
        <span class="rep-work-badge">${w.dynasty || ''}</span>
        <span class="rep-work-author author-bio-link" onclick="showAuthorBio('${(w.author || '').replace(/'/g, "\\'")}')">${w.author || ''}</span>
        <span class="rep-work-title">《${w.title.split('·').length > 1 ? w.title.split('·')[1] : w.title}》</span>
      </div>
      <div class="rep-work-text">${workHtml}</div>
    </div>
  `;
  
  contentDiv.innerHTML = html;
  repDiv.style.display = 'block';
}

// 按传统词牌格式化代表作内容（分行展示，上下阕间空行）
function formatWorkContent(content) {
  if (!content) return '';
  
  // 直接按换行符分行展示（代表作文本已有正确的换行符）
  const lines = content.split('\n');
  
  let html = '';
  for (const line of lines) {
    if (line.trim() === '') {
      // 空行 = 上下阕分界
      html += '<br>';
    } else {
      html += `<span class="rep-line">${escHtml(line)}</span><br>`;
    }
  }
  
  // 移除末尾多余的<br>
  if (html.endsWith('<br>')) {
    html = html.slice(0, -4);
  }
  
  return html;
}

// （startFillCompose 已移除 - 代表作和填词区域现在同页面展示）



// 显示作品详情
async function showWorkDetail(patternIndex, workIndex) {
  const cipaiId = ComposeData.selectedCipaiId;
  const res = await api(`/api/cipai/${cipaiId}/representatives?pattern=${patternIndex}`);
  
  if (!res.success || !res.data.works || !res.data.works[workIndex]) {
    toast('加载作品详情失败', 'error');
    return;
  }
  
  const work = res.data.works[workIndex];
  const pattern = ComposeData.selectedCipai.patterns[patternIndex];
  
  // 显示作品详情模态框
  const content = `
    <div class="work-detail">
      <div class="work-detail-header">
        <span class="work-detail-badge">${work.dynasty || ''}</span>
        <span class="work-detail-author author-bio-link" onclick="showAuthorBio('${(work.author || '').replace(/'/g, "\\'")}')">${work.author || ''}</span>
      </div>
      <h3 class="work-detail-title">${work.title}</h3>
      <div class="work-detail-pattern">${pattern.name || `格律${patternIndex + 1}`}</div>
      <div class="work-detail-content">${(work.text || work.content || '').replace(/\n/g, '<br>')}</div>
    </div>
  `;
  
  // 创建模态框
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.onclick = (e) => {
    if (e.target === modal) modal.remove();
  };
  modal.innerHTML = `
    <div class="modal-content work-detail-modal">
      <div class="modal-header">
        <h3>作品详情</h3>
        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
      </div>
      <div class="modal-body">${content}</div>
    </div>
  `;
  document.body.appendChild(modal);
}

// 渲染填词格子
function renderComposeGrid() {
  const container = document.getElementById('composeGrid');
  const totalSentences = ComposeData.grid.length;
  const lineGroups = ComposeData.lineGroups || [];  // 按韵脚分行分组
  const stanzaSplit = ComposeData.stanzaSplit;  // 上阕句数

  let html = '';

  // 计算上阕最后一行的索引（上阕句子范围：0 ~ stanzaSplit-1）
  let lastUpperLineIdx = -1;
  if (lineGroups.length > 0 && stanzaSplit) {
    let sentCount = 0;
    for (let li = 0; li < lineGroups.length; li++) {
      sentCount += lineGroups[li].length;
      if (sentCount >= stanzaSplit) {
        lastUpperLineIdx = li;
        break;
      }
    }
  }

  lineGroups.forEach((group, lineIdx) => {
    // 判断是否需要上阕/下阕标记
    let stanzaLabel = '';
    const firstSentIdx = group[0];
    if (firstSentIdx === 0) {
      stanzaLabel = '上阕';
    } else if (stanzaSplit && firstSentIdx >= stanzaSplit && lineIdx === lastUpperLineIdx + 1) {
      stanzaLabel = '下阕';
    } else if (!stanzaSplit && firstSentIdx === Math.ceil(totalSentences / 2) && totalSentences > 4) {
      stanzaLabel = '下阕';
    }

    // 上阕与下阕之间加分隔线
    if (stanzaSplit && lineIdx === lastUpperLineIdx + 1) {
      html += '<div class="stanza-gap"></div>';
    } else if (!stanzaSplit && lineIdx > 0 && firstSentIdx === Math.ceil(totalSentences / 2)) {
      html += '<div class="stanza-gap"></div>';
    }

    // 上下阕标签独占一行
    if (stanzaLabel) {
      html += `<div class="stanza-label-row"><span class="stanza-marker">${stanzaLabel}</span></div>`;
    }

    // 渲染一行（可能包含多个句子）
    html += '<div class="compose-line">';

    group.forEach((sIdx, sOffset) => {
      const sentence = ComposeData.grid[sIdx];
      html += `
        <div class="sentence-inline" data-sentence-index="${sIdx}">
          ${sentence.chars.map((char, cIdx) => {
            const multiGroup = ComposeData.rhymeGroups && ComposeData.rhymeGroups.length > 1;
            const rhymeGroupClass = getRhymeGroupClass(
              char.rhyme_group_index !== undefined ? char.rhyme_group_index : 0,
              char.is_rhyme,
              multiGroup
            );
            return `
            <div class="char-cell-wrapper">
              <div class="char-cell">
                <div class="char-tone-hint" data-tone="${char.expected_tone}">${char.expected_tone}</div>
                <input type="text"
                       class="char-input ${rhymeGroupClass}"
                       maxlength="1"
                       data-global-index="${char.global_index}"
                       data-local-index="${char.local_index}"
                       data-sentence-index="${sIdx}"
                       data-expected="${char.expected_tone}"
                       data-is-rhyme="${char.is_rhyme}"
                       data-rhyme-group="${char.is_rhyme ? (char.rhyme_group_index !== undefined ? char.rhyme_group_index : 0) : ''}"
                       oninput="onCharInput(this)"
                       onkeydown="onCharKeydown(event, this)">
                <div class="char-pinyin" id="pinyin-${char.global_index}"></div>
              </div>
              ${char.punctuation_after ? `<span class="char-punctuation">${char.punctuation_after}</span>` : ''}
            </div>
          `}).join('')}
        </div>
      `;
      // 在句子之间（非末尾句子）插入句子级标点
      if (sOffset < group.length - 1 && sentence.punctuation) {
        html += `<span class="char-punctuation">${sentence.punctuation}</span>`;
      }
    });

    html += '</div>';  // .compose-line
  });

  // 如果没有lineGroups数据，回退到旧方式
  if (lineGroups.length === 0) {
    html = '';
    ComposeData.grid.forEach((sentence, sIdx) => {
      const halfPoint = Math.ceil(totalSentences / 2);
      let stanzaLabel = '';
      if (sIdx === 0) stanzaLabel = '<span class="stanza-marker">上阕</span>';
      else if (sIdx === halfPoint && totalSentences > 4) stanzaLabel = '<span class="stanza-marker">下阕</span>';

      html += `
        <div class="sentence-block">
          <div class="sentence-label">
            ${stanzaLabel}
            第${sIdx + 1}句（${sentence.char_count}字）
          </div>
          <div class="char-cells">
            ${sentence.chars.map((char, cIdx) => {
              const multiGroup = ComposeData.rhymeGroups && ComposeData.rhymeGroups.length > 1;
              const rhymeGroupClass = getRhymeGroupClass(
                char.rhyme_group_index !== undefined ? char.rhyme_group_index : 0,
                char.is_rhyme,
                multiGroup
              );
              return `
              <div class="char-cell-wrapper">
                <div class="char-cell">
                  <div class="char-tone-hint" data-tone="${char.expected_tone}">${char.expected_tone}</div>
                  <input type="text"
                         class="char-input ${rhymeGroupClass}"
                         maxlength="1"
                         data-global-index="${char.global_index}"
                         data-local-index="${char.local_index}"
                         data-sentence-index="${sIdx}"
                         data-expected="${char.expected_tone}"
                         data-is-rhyme="${char.is_rhyme}"
                         data-rhyme-group="${char.is_rhyme ? (char.rhyme_group_index !== undefined ? char.rhyme_group_index : 0) : ''}"
                         oninput="onCharInput(this)"
                         onkeydown="onCharKeydown(event, this)">
                  <div class="char-pinyin" id="pinyin-${char.global_index}"></div>
                </div>
                ${char.punctuation_after ? `<span class="char-punctuation">${char.punctuation_after}</span>` : ''}
              </div>
            `}).join('')}
          </div>
        </div>
      `;
    });
  }

  container.innerHTML = html;

  // 重置反馈
  document.getElementById('pingzeStatus').textContent = '等待输入...';
  document.getElementById('rhymeStatus').textContent = '等待输入...';
}

// 字符输入事件
async function onCharInput(input) {
  const char = input.value.trim();
  const globalIdx = parseInt(input.dataset.globalIndex);
  const expectedTone = input.dataset.expected;
  const isRhyme = input.dataset.isRhyme === 'true';
  const rhymeGroupIdx = input.dataset.rhymeGroup !== '' ? parseInt(input.dataset.rhymeGroup) : null;
  
  if (!char) {
    // 清空
    delete ComposeData.userChars[globalIdx];
    input.classList.remove('error');
    document.getElementById(`pinyin-${globalIdx}`).textContent = '';
    
    // 如果清空的是韵脚字，按韵组独立检查
    if (isRhyme && rhymeGroupIdx !== null) {
      const rg = ComposeData.rhymeGroups.find(g => g.index === rhymeGroupIdx);
      if (rg) {
        // 检查该韵组内是否所有韵脚字都被清空
        const remainingInGroup = rg.positions.filter(pos => ComposeData.userChars[pos]);
        if (remainingInGroup.length === 0) {
          // 该韵组所有韵脚字都清空，清除该韵组提示
          delete ComposeData.rhymeGroupData[rhymeGroupIdx];
          renderRhymeHintContent();
        } else {
          // 该组还有字，检查baseChar是否被清空
          const groupData = ComposeData.rhymeGroupData[rhymeGroupIdx];
          if (groupData && groupData.baseChar === ComposeData.userChars[globalIdx]) {
            // baseChar被清空，切换到组内第一个剩余字
            const firstRemaining = remainingInGroup
              .map(pos => ({ pos, char: ComposeData.userChars[pos] }))
              .sort((a, b) => rg.positions.indexOf(a.pos) - rg.positions.indexOf(b.pos))[0];
            if (firstRemaining) {
              showRhymeHint(firstRemaining.char, rhymeGroupIdx);
            }
          }
        }
      }
      // 检查是否所有韵组都清空了
      const anyGroupActive = ComposeData.rhymeGroups.some(g => {
        const remaining = g.positions.filter(pos => ComposeData.userChars[pos]);
        return remaining.length > 0;
      });
      if (!anyGroupActive) {
        document.getElementById('rhymeHint').style.display = 'none';
      }
    }
    
    updateFeedback();
    return;
  }
  
  // 检查是否为汉字
  if (!/^[\u4e00-\u9fff]$/.test(char)) {
    input.value = '';
    toast('请输入汉字', 'error');
    return;
  }
  
  // 韵脚替换检测：如果该位置之前已有字且是韵脚，先清除旧字对韵组的影响
  const oldChar = ComposeData.userChars[globalIdx];
  if (isRhyme && rhymeGroupIdx !== null && oldChar && oldChar !== char) {
    // 该韵脚位置有旧字被新字替换，先移除旧字的影响
    const rg = ComposeData.rhymeGroups.find(g => g.index === rhymeGroupIdx);
    const groupData = ComposeData.rhymeGroupData[rhymeGroupIdx];
    if (rg && groupData) {
      // 检查替换后该韵组是否还有其他字（不含当前位置）
      const otherPositionsInGroup = rg.positions.filter(pos => pos !== globalIdx && ComposeData.userChars[pos]);
      if (otherPositionsInGroup.length === 0) {
        // 替换后该韵组没有其他字了，清除韵组数据，让新字重新建立
        delete ComposeData.rhymeGroupData[rhymeGroupIdx];
      } else if (groupData.baseChar === oldChar) {
        // 旧字是baseChar，需要切换baseChar到组内其他字
        const newBasePos = otherPositionsInGroup
          .sort((a, b) => rg.positions.indexOf(a) - rg.positions.indexOf(b))[0];
        const newBaseChar = ComposeData.userChars[newBasePos];
        // 重新建立韵组提示（以新baseChar为准）
        await showRhymeHint(newBaseChar, rhymeGroupIdx);
      }
      // 如果旧字不是baseChar，无需额外处理，直接让新字参与冲突检测即可
    }
  }
  
  // 保存用户输入
  ComposeData.userChars[globalIdx] = char;
  
  // 检查平仄
  try {
    // 获取该韵组的baseChar（如果有），注意：如果是替换且baseChar被清除，此时baseChar应为null
    let rhymeBaseChar = null;
    if (isRhyme && rhymeGroupIdx !== null) {
      rhymeBaseChar = ComposeData.rhymeGroupData[rhymeGroupIdx]?.baseChar || null;
    }
    
    const checkRes = await api('/api/check/char', 'POST', {
      char,
      expected_tone: expectedTone,
      rhyme_base_char: rhymeBaseChar
    });
    
    if (checkRes.success) {
      const data = checkRes.data;
      
      // 显示拼音
      document.getElementById(`pinyin-${globalIdx}`).textContent = data.pinyin;
      
      // 平仄检查
      let pingzeMatch = data.pingze_match;
      
      // 韵格增强验证：检查韵脚字的声调是否与韵格要求一致
      if (isRhyme && pingzeMatch) {
        const rs = ComposeData.rhymeScheme;
        if (rs) {
          const actualTone = data.actual_tone; // '平' 或 '仄'
          const schemeType = rs.type;
          
          // 平韵格：韵脚必须是平声
          if (schemeType === 'ping_yun_ge' && actualTone !== '平') {
            pingzeMatch = false;
            toast(`平韵格韵脚应为平声字，"${char}"为仄声`, 'warning');
          }
          // 仄韵格：韵脚必须是仄声（排除叶韵的情况）
          else if (schemeType === 'ze_yun_ge' && actualTone !== '仄' && !rs.is_ye_rhyme) {
            pingzeMatch = false;
            toast(`仄韵格韵脚应为仄声字，"${char}"为平声`, 'warning');
          }
        }
      }
      
      if (!pingzeMatch) {
        input.classList.add('error');
      } else {
        input.classList.remove('error');
      }
      
      // 韵脚处理
      if (isRhyme && rhymeGroupIdx !== null) {
        const groupData = ComposeData.rhymeGroupData[rhymeGroupIdx];
        if (!groupData || !groupData.baseChar) {
          // 这是该韵组的第一个韵脚字（或替换后韵组被重置）
          showRhymeHint(char, rhymeGroupIdx);
        } else {
          // 检查该韵组内的韵脚冲突
          checkRhymeConflict(char, input, rhymeGroupIdx);
        }
      }
    }
  } catch (e) {
    console.error('检查字符失败:', e);
  }
  
  // 更新反馈
  updateFeedback();
  
  // 自动跳到下一个格子
  moveToNextInput(input);
}

// 键盘事件
function onCharKeydown(event, input) {
  if (event.key === 'Backspace' && !input.value) {
    // 退格键且当前为空，跳到前一个格子
    moveToPrevInput(input);
  } else if (event.key === 'ArrowLeft') {
    moveToPrevInput(input);
  } else if (event.key === 'ArrowRight') {
    moveToNextInput(input);
  }
}

// 移动到下一个输入框
function moveToNextInput(currentInput) {
  const inputs = Array.from(document.querySelectorAll('.char-input'));
  const currentIdx = inputs.indexOf(currentInput);
  if (currentIdx < inputs.length - 1) {
    inputs[currentIdx + 1].focus();
  }
}

// 移动到上一个输入框
function moveToPrevInput(currentInput) {
  const inputs = Array.from(document.querySelectorAll('.char-input'));
  const currentIdx = inputs.indexOf(currentInput);
  if (currentIdx > 0) {
    inputs[currentIdx - 1].focus();
  }
}

// 显示韵脚提示（按韵组独立）
async function showRhymeHint(char, groupIndex) {
  const hintDiv = document.getElementById('rhymeHint');
  hintDiv.style.display = 'block';
  
  // 获取该韵组信息
  const rg = ComposeData.rhymeGroups.find(g => g.index === groupIndex);
  const typeLabel = rg ? (rg.type + '韵') : '韵';
  
  // 显示加载中
  renderRhymeHintGroupLoading(groupIndex, typeLabel);
  
  // 获取平水韵信息
  const res = await api(`/api/rhyme/yunbu?char=${char}`);
  if (res.success) {
    const data = res.data;
    
    if (data.yunbus && data.yunbus.length > 0) {
      // 构建韵组显示名
      let yunbuDisplay;
      const compatYunbus = data.compat_yunbus || [];
      if (compatYunbus.length > 1) {
        yunbuDisplay = compatYunbus.join('') + '通用';
      } else if (data.yunbus.length === 1) {
        yunbuDisplay = data.yunbus[0];
      } else {
        yunbuDisplay = `${data.yunbus[0]}【${data.yunbus.slice(1).join('、')}】`;
      }
      
      // 保存该韵组数据
      ComposeData.rhymeGroupData[groupIndex] = {
        baseChar: char,
        yunbuDisplay: yunbuDisplay,
        compatYunbus: compatYunbus,
        yunbuChars: data.yunbu_chars || [],
        fallback: false
      };
      
    } else if (data.fallback && data.yunbu_chars && data.yunbu_chars.length > 0) {
      // 降级显示
      ComposeData.rhymeGroupData[groupIndex] = {
        baseChar: char,
        yunbuDisplay: data.rhyme_group_label || '简化韵组',
        compatYunbus: [],
        yunbuChars: data.yunbu_chars || [],
        fallback: true
      };
      
    } else {
      ComposeData.rhymeGroupData[groupIndex] = {
        baseChar: char,
        yunbuDisplay: '未收录',
        compatYunbus: [],
        yunbuChars: [],
        fallback: false,
        message: data.message || '该字不在平水韵数据库中'
      };
    }
  } else {
    ComposeData.rhymeGroupData[groupIndex] = {
      baseChar: char,
      yunbuDisplay: '查询失败',
      compatYunbus: [],
      yunbuChars: [],
      fallback: false,
      message: '请稍后重试'
    };
  }
  
  // 渲染所有韵组提示
  renderRhymeHintContent();
}

// 渲染韵组加载中状态
function renderRhymeHintGroupLoading(groupIndex, typeLabel) {
  renderRhymeHintContent();
}

// 渲染所有韵组提示内容
function renderRhymeHintContent() {
  const container = document.getElementById('rhymeHintContent');
  if (!container) return;
  
  // 检查是否有任何活跃韵组
  const activeGroups = ComposeData.rhymeGroups.filter(g => {
    return g.positions.some(pos => ComposeData.userChars[pos]);
  });
  
  if (activeGroups.length === 0) {
    document.getElementById('rhymeHint').style.display = 'none';
    container.innerHTML = '';
    return;
  }
  
  let html = '';
  
  const multiGroup = ComposeData.rhymeGroups && ComposeData.rhymeGroups.length > 1;
  
  activeGroups.forEach((rg, idx) => {
    const groupData = ComposeData.rhymeGroupData[rg.index];
    const rs = ComposeData.rhymeScheme;
    
    // 根据韵格类型构建标签
    let typeLabel = '韵组';
    if (rs) {
      const schemeType = rs.type;
      if (schemeType === 'que_jian') {
        // 阕间换韵：标记上阕/下阕
        const stanzaInfo = rg.type === '平' ? '平韵' : '仄韵';
        // 用positions判断上下阕
        const stanzaSplit = ComposeData.stanzaSplit;
        const firstPos = rg.positions[0];
        const stanzaLabel = stanzaSplit && firstPos < stanzaSplit ? '上阕' : '下阕';
        typeLabel = `${stanzaLabel}${stanzaInfo}`;
      } else if (schemeType === 'que_nei' || schemeType === 'que_nei_jian') {
        typeLabel = `${rg.type}韵组${idx + 1}`;
      } else {
        typeLabel = rg.type + '韵';
      }
    } else if (multiGroup) {
      typeLabel = rg.type + '韵组';
    }
    
    const colorClass = multiGroup ? getRhymeGroupLabelClass(rg.index) : '';
    const separator = idx > 0 ? '<div class="rhyme-group-separator"></div>' : '';
    
    html += separator;
    html += `<div class="rhyme-group-block" data-rhyme-group="${rg.index}">`;
    html += `<div class="rhyme-group-header">`;
    html += `<span class="rhyme-group-type ${colorClass}">${typeLabel}</span>`;
    
    if (groupData) {
      html += `<span class="rhyme-group-name ${colorClass}">${groupData.yunbuDisplay || '识别中...'}</span>`;
    } else {
      html += `<span class="rhyme-group-name">等待输入...</span>`;
    }
    html += `</div>`;
    
    // 可用韵脚字
    html += `<div class="rhyme-group-chars">`;
    if (groupData && groupData.yunbuChars && groupData.yunbuChars.length > 0) {
      // 收集该韵组内已使用的字
      const usedChars = new Set();
      rg.positions.forEach(pos => {
        if (ComposeData.userChars[pos]) {
          usedChars.add(ComposeData.userChars[pos]);
        }
      });
      
      groupData.yunbuChars.forEach(c => {
        const usedClass = usedChars.has(c) ? ' used' : '';
        const title = usedChars.has(c) ? ' title="已使用"' : '';
        html += `<span class="rhyme-char${usedClass}"${title}>${c}</span>`;
      });
    } else if (groupData && groupData.message) {
      html += `<span class="rhyme-char-message">${groupData.message}</span>`;
    } else if (groupData) {
      html += `<span class="rhyme-char-message">加载中...</span>`;
    } else {
      html += `<span class="rhyme-char-message">等待输入第一个韵脚字</span>`;
    }
    html += `</div>`;
    html += `</div>`;
  });
  
  container.innerHTML = html;
}

// 检查韵脚冲突（按韵组独立）
async function checkRhymeConflict(newChar, input, groupIndex) {
  const rg = ComposeData.rhymeGroups.find(g => g.index === groupIndex);
  if (!rg) return;
  
  // 仅收集该韵组内已填的韵脚字
  const groupData = ComposeData.rhymeGroupData[groupIndex];
  const rhymeChars = [];
  if (groupData && groupData.baseChar) {
    rhymeChars.push(groupData.baseChar);
  }
  rg.positions.forEach(pos => {
    const ch = ComposeData.userChars[pos];
    if (ch && (!groupData || ch !== groupData.baseChar)) {
      rhymeChars.push(ch);
    }
  });
  rhymeChars.push(newChar);
  
  // 调用冲突检测API
  const res = await api('/api/rhyme/check-conflict', 'POST', { chars: rhymeChars });
  
  if (res.success && res.data.has_conflict) {
    input.classList.add('error');
    toast(`韵脚矛盾："${newChar}"与同组已填韵脚字不在同一韵部（含通用韵组）`, 'error');
  } else if (res.success && res.data.compat_yunbus && res.data.compat_yunbus.length > 0) {
    // 更新该韵组的韵部显示
    const compatYunbus = res.data.compat_yunbus;
    const display = compatYunbus.length > 1 
      ? compatYunbus.join('') + '通用'
      : compatYunbus[0];
    
    if (ComposeData.rhymeGroupData[groupIndex]) {
      ComposeData.rhymeGroupData[groupIndex].yunbuDisplay = display;
      ComposeData.rhymeGroupData[groupIndex].compatYunbus = compatYunbus;
    }
  }
  
  // 更新韵脚字显示（标记已使用的字）
  renderRhymeHintContent();
}

// 更新韵脚字显示（由renderRhymeHintContent统一处理，保留兼容）
function updateRhymeCharsDisplay() {
  renderRhymeHintContent();
}

// 更新实时反馈
function updateFeedback() {
  const totalChars = ComposeData.grid.reduce((sum, s) => sum + s.char_count, 0);
  const filledCount = Object.keys(ComposeData.userChars).length;
  
  // 统计平仄错误
  const errorCount = document.querySelectorAll('.char-input.error').length;
  
  // 统计韵脚
  const rhymeCount = ComposeData.rhymePositions.filter(pos => ComposeData.userChars[pos]).length;
  const totalRhyme = ComposeData.rhymePositions.length;
  
  // 平仄反馈
  const pingzeStatus = document.getElementById('pingzeStatus');
  if (filledCount === 0) {
    pingzeStatus.textContent = '等待输入...';
    pingzeStatus.className = '';
  } else if (errorCount === 0) {
    pingzeStatus.textContent = `已填${filledCount}/${totalChars}字，平仄全部正确 ✓`;
    pingzeStatus.className = 'success';
  } else {
    pingzeStatus.textContent = `已填${filledCount}/${totalChars}字，${errorCount}处平仄不符（已标红）`;
    pingzeStatus.className = 'warning';
  }
  
  // 韵脚反馈
  const rhymeStatus = document.getElementById('rhymeStatus');
  const activeGroupData = Object.values(ComposeData.rhymeGroupData).filter(g => g.baseChar);
  const rs = ComposeData.rhymeScheme;
  const schemeLabel = rs ? `【${rs.name}】` : '';
  if (activeGroupData.length === 0) {
    rhymeStatus.textContent = `${schemeLabel}已填${rhymeCount}/${totalRhyme}个韵脚，等待确定韵组...`;
    rhymeStatus.className = '';
  } else {
    const groupTexts = activeGroupData.map(g => g.yunbuDisplay || '识别中').join('、');
    rhymeStatus.textContent = `${schemeLabel}韵组：${groupTexts}，已填${rhymeCount}/${totalRhyme}个韵脚`;
    rhymeStatus.className = 'success';
  }
}

// 清空重填
function clearCompose() {
  if (!confirm('确定要清空所有填写的内容吗？')) return;
  
  ComposeData.userChars = {};
  ComposeData.rhymeGroupData = {};
  
  document.querySelectorAll('.char-input').forEach(input => {
    input.value = '';
    input.classList.remove('error');
  });
  
  document.querySelectorAll('.char-pinyin').forEach(el => {
    el.textContent = '';
  });
  
  document.getElementById('rhymeHint').style.display = 'none';
  const rhymeContent = document.getElementById('rhymeHintContent');
  if (rhymeContent) rhymeContent.innerHTML = '';
  updateFeedback();
}

// 重置填词（重新选择词牌）
function resetCompose() {
  ComposeData = {
    selectedCipaiId: null,
    selectedCipai: null,
    selectedPatternIndex: 0,
    grid: null,
    rhymePositions: [],
    rhymeGroups: [],
    rhymeGroupData: {},
    lineGroups: [],
    stanzaSplit: null,
    userChars: {},
    patternWorks: {}  // 缓存格律代表作
  };
  
  document.getElementById('composeStep1').style.display = 'block';
  document.getElementById('composeStep1_5').style.display = 'none';
  document.getElementById('composeStep2').style.display = 'none';
  document.getElementById('composeRepWork').style.display = 'none';
  
  // 清空搜索框
  document.getElementById('composeCipaiSearch').value = '';
  loadComposeCipaiList();
}

// 完成填词，跳转到评分
function submitCompose() {
  const totalChars = ComposeData.grid.reduce((sum, s) => sum + s.char_count, 0);
  const filledCount = Object.keys(ComposeData.userChars).length;
  
  if (filledCount < totalChars) {
    toast(`还有${totalChars - filledCount}个字未填写`, 'error');
    return;
  }
  
  // 构建词作文本（按韵脚分行，上下阕间空行）
  let content = '';
  const lineGroups = ComposeData.lineGroups || [];
  const stanzaSplit = ComposeData.stanzaSplit;
  
  if (lineGroups.length > 0) {
    // 按韵脚分行构建
    let lastUpperLineIdx = -1;
    if (stanzaSplit) {
      let sentCount = 0;
      for (let li = 0; li < lineGroups.length; li++) {
        sentCount += lineGroups[li].length;
        if (sentCount >= stanzaSplit) {
          lastUpperLineIdx = li;
          break;
        }
      }
    }
    
    lineGroups.forEach((group, lineIdx) => {
      const lineText = group.map(sIdx => {
        const sentence = ComposeData.grid[sIdx];
        return sentence.chars.map(char => ComposeData.userChars[char.global_index] || '').join('');
      }).join('');
      const punct = ComposeData.grid[group[group.length - 1]].punctuation || '。';
      content += lineText + punct;
      
      // 上下阕之间空行
      if (stanzaSplit && lineIdx === lastUpperLineIdx) {
        content += '\n\n';
      } else if (lineIdx < lineGroups.length - 1) {
        content += '\n';
      }
    });
  } else {
    // 回退到旧方式
    ComposeData.grid.forEach((sentence, sIdx) => {
      const line = sentence.chars.map(char => ComposeData.userChars[char.global_index] || '').join('');
      content += line;
      if (sIdx === Math.floor(ComposeData.grid.length / 2) - 1) {
        content += '\n\n';
      } else {
        content += '\n';
      }
    });
  }
  
  // 跳转到评分页面并填入内容
  showPage('score');
  
  // 选择词牌
  const cipai = App.cipaiList.find(c => c.id === ComposeData.selectedCipaiId);
  if (cipai) selectCipai(cipai);
  
  // 填入内容
  document.getElementById('poemContent').value = content.trim();
  document.getElementById('charCount').textContent = filledCount;
  document.getElementById('editWorkId').value = '';
  
  toast('已填入词作，可以开始评分了', 'success');
}

