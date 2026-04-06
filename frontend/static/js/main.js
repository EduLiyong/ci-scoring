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
      if (extra.length > 0) {
        return `<span class="rep-work-author">${name}</span><span class="rep-work-zi-hao">（${extra.join('，')}）</span>`;
      }
      return `<span class="rep-work-author">${name}</span>`;
    }

    // 存储当前数据和词牌ID供编辑使用
    window._repWorksData = data;
    window._repCipaiId = cipaiId;
    const isEdu = App.currentUser && App.currentUser.username.toLowerCase() === 'edu';

    // 正体代表作
    if (data.main && data.main.length > 0) {
      html += `<div class="rep-section">
        <div class="rep-section-title">正体代表作</div>
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
    }

    // 变体代表作
    if (data.variants && data.variants.length > 0) {
      data.variants.forEach((v) => {
        if (!v.works || v.works.length === 0) return;
        html += `<div class="rep-section">
          <div class="rep-section-title">变体代表作 · ${v.name || ''}</div>
          ${v.works.map(w => `
            <div class="rep-work">
              <div class="rep-work-header">
                <span class="rep-work-title">${w.title || '无题'}</span>
                ${w.dynasty ? `<span class="rep-work-dynasty">${w.dynasty}</span>` : ''}
                ${fmtAuthor(w)}
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
function editRepWork(index, type) {
  const data = window._repWorksData;
  const cipaiId = window._repCipaiId;
  
  if (type !== 'main') {
    showToast('暂不支持编辑变体代表作', 'info');
    return;
  }
  
  const work = data.main[index];
  
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

  const workData = { title, author, dynasty, zi, hao, text };
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
